import asyncio
import json

import aiohttp
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from helpers.custom_logger import CustomLogger
from opentelemetry import baggage, trace
from opentelemetry.baggage import set_baggage
from opentelemetry.baggage.propagation import W3CBaggagePropagator
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

resource = Resource(attributes={SERVICE_NAME: "web-server"})
traces_endpoint = "http://jaeger:4318/v1/traces"

trace_provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=traces_endpoint))
trace_provider.add_span_processor(processor)
trace.set_tracer_provider(trace_provider)

tracer = trace.get_tracer("web-server.trace")
app = FastAPI()
logger = CustomLogger().get_logger()

service_name = "pre-processor-service"
port = "5001"


@app.post("/inference")
async def inference(image: UploadFile):
    with tracer.start_as_current_span("webserver-request") as span:
        try:
            span.set_attribute("http.method", "POST")
            span.set_attribute("file.name", image.filename)
            span.set_attribute("file.size", image.size)

            set_baggage("Web-server", "check")

            async with aiohttp.ClientSession() as session:
                for attempt in range(3):  # Retry up to 3 times
                    try:
                        form_data = aiohttp.FormData()
                        form_data.add_field(
                            "image",
                            await image.read(),
                            filename=image.filename,
                            content_type=image.content_type,
                        )

                        ctx = baggage.set_baggage("Web-server", "check")
                        headers = {}
                        W3CBaggagePropagator().inject(headers, ctx)
                        TraceContextTextMapPropagator().inject(headers, ctx)

                        async with session.post(
                            f"http://{service_name}:{port}/process",
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

                json_data = json.loads(response_text)
                json_data["success"] = "true"
                span.set_attribute("response.success", "true")
                result = json_data

        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.status.Status(trace.status.StatusCode.ERROR, str(e)))
            logger.exception(f"Some error occurred: {e}")
            result = {"error": "Some error occurred in downstream service"}

        return JSONResponse(content=result, status_code=200)
