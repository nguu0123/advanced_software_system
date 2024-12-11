import os
import shutil
import sys

from darknet import get_tiny_yolo_detection
from fastapi import FastAPI, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse
from opentelemetry import trace
from opentelemetry.baggage.propagation import W3CBaggagePropagator
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Status, StatusCode
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from pydantic import BaseModel
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "/inference/temp"
TRACES_ENDPOINT = "http://jaeger:4318/v1/traces"

resource = Resource(attributes={SERVICE_NAME: "inference-server"})
trace_provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=TRACES_ENDPOINT))
trace_provider.add_span_processor(processor)
trace.set_tracer_provider(trace_provider)

tracer = trace.get_tracer("inference-server.trace")

app = FastAPI()
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


class InferenceResponse(BaseModel):
    result: dict


@app.post("/inference", response_model=InferenceResponse)
async def ml_inference_service(image: UploadFile, request: Request):
    headers = dict(request.headers)
    carrier = {"traceparent": headers["traceparent"]}
    ctx = TraceContextTextMapPropagator().extract(carrier=carrier)

    b2 = {"baggage": headers["baggage"]}
    ctx2 = W3CBaggagePropagator().extract(b2, context=ctx)

    with tracer.start_as_current_span(
        "inference-service-request", context=ctx2
    ) as span:
        if not image.filename:
            span.set_status(Status(StatusCode.ERROR, "Empty filename provided"))
            raise HTTPException(status_code=400, detail="No image file provided")

        filename = secure_filename(image.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            span.add_event("File saved", {"file_path": file_path})

            span.add_event("Starting inference")
            result = get_tiny_yolo_detection(file_path)
            span.add_event("Inference completed", {"result": result})

            response_data = {"result": result}
            span.set_status(Status(StatusCode.OK))

        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, f"Inference error: {e}"))
            sys.stderr.write(f"Error occurred during inference: {e}\n")
            raise HTTPException(status_code=500, detail=f"Inference error: {e}")

        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
                span.add_event("File cleaned up", {"file_path": file_path})

        return JSONResponse(content=response_data, status_code=200)
