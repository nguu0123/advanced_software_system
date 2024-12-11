import asyncio
import json
import uuid
from io import BytesIO

import aiohttp
from fastapi import FastAPI, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse
from helpers.custom_logger import CustomLogger
from opentelemetry import baggage, trace
from opentelemetry.baggage import set_baggage
from opentelemetry.baggage.propagation import W3CBaggagePropagator
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.propagate import extract
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from PIL import Image, ImageEnhance

resource = Resource(attributes={SERVICE_NAME: "pre-processor"})
traces_endpoint = "http://jaeger:4318/v1/traces"

trace_provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=traces_endpoint))
trace_provider.add_span_processor(processor)
trace.set_tracer_provider(trace_provider)

tracer = trace.get_tracer("pre-processor.trace")

app = FastAPI()
logger = CustomLogger().get_logger()

counter = 0
edge_inference_service_name = "inference-service"
edge_inference_port = "5002"


@app.post("/process")
async def inference(image: UploadFile, request: Request):
    job_id = uuid.uuid4().hex

    try:
        # Preprocess the image
        img = Image.open(BytesIO(await image.read()))
        preprocessed_data = preprocess(img)

        # Determine inference server
        service_name, port = get_inference_server()

        # Extract trace and baggage context from incoming request headers
        carrier = {"traceparent": request.headers.get("traceparent", "")}
        baggage_carrier = {"baggage": request.headers.get("baggage", "")}
        parent_context = extract(carrier)
        context_with_baggage = extract(baggage_carrier, context=parent_context)

        # Start tracing the preprocessing request
        with tracer.start_as_current_span(
            "preprocess-request", context=context_with_baggage
        ) as span:
            span.set_attribute("http.method", request.method)
            span.set_attribute("job.id", job_id)
            span.set_attribute("file.name", image.filename)
            span.set_attribute("file.size", image.size)

            # Set baggage for downstream services
            set_baggage("pre-processor", "check")

            # Prepare headers for downstream call
            #
            ctx = baggage.set_baggage("Pre-processor", "check")
            headers = {}
            W3CBaggagePropagator().inject(headers, ctx)
            TraceContextTextMapPropagator().inject(headers, ctx)

            # Make the downstream request with retries
            async with aiohttp.ClientSession() as session:
                for attempt in range(3):  # Retry up to 3 times
                    try:
                        form_data = aiohttp.FormData()
                        form_data.add_field(
                            "image",
                            preprocessed_data,
                            filename=image.filename,
                            content_type=image.content_type,
                        )

                        async with session.post(
                            f"http://{service_name}:{port}/inference",
                            data=form_data,
                            headers=headers,
                        ) as response:
                            span.set_attribute(
                                "downstream.status_code", response.status
                            )
                            if response.status == 200:
                                response_text = await response.text()
                                span.add_event(
                                    "successful_response", {"response": response_text}
                                )
                                break
                            logger.warning(
                                f"Received non-200 status: {response.status}"
                            )
                            await asyncio.sleep(0.1)
                    except aiohttp.ClientError as e:
                        span.record_exception(e)
                        logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                        await asyncio.sleep(0.1)
                else:
                    span.set_status(
                        trace.status.Status(
                            trace.status.StatusCode.ERROR,
                            "Downstream service unavailable",
                        )
                    )
                    raise HTTPException(
                        status_code=500, detail="Downstream service unavailable"
                    )

            # Prepare response with tracing metadata
            json_data = {"data": json.loads(response_text)}
            json_data["uid"] = job_id
            return JSONResponse(content=json_data, status_code=200)

    except Exception as e:
        # Record exceptions in the trace and log the error
        with tracer.start_as_current_span("error-handling") as error_span:
            error_span.record_exception(e)
            error_span.set_status(
                trace.status.Status(trace.status.StatusCode.ERROR, str(e))
            )
        logger.exception(f"Error processing request: {e}")
        return JSONResponse(
            content={"error": "An error occurred during processing"}, status_code=500
        )


@app.get("/process")
async def process_get():
    return JSONResponse(content={"error": "method not allowed"}, status_code=405)


def preprocess(img: Image.Image) -> BytesIO:
    """Applies image enhancement and returns a byte stream of the modified image."""
    enhancer = ImageEnhance.Sharpness(img)
    enhanced_img = enhancer.enhance(1.2)
    byte_io = BytesIO()
    enhanced_img.save(byte_io, "JPEG")
    byte_io.seek(0)
    return byte_io


def get_inference_server():
    """Returns the inference server's name and port."""
    return edge_inference_service_name, edge_inference_port
