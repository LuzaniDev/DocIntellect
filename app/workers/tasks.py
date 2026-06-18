import asyncio
import logging

from app.pipeline.orchestrator import PipelineOrchestrator
from app.workers import celery_app

logger = logging.getLogger(__name__)
orchestrator = PipelineOrchestrator()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_document_task(self, file_path: str) -> dict:
    logger.info(f"Task: processando documento {file_path}")

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(orchestrator.process_document(file_path))
        loop.close()

        return {
            "status": "completed",
            "document_type": result.document_type,
            "fields_count": len(result.fields),
            "overall_confidence": result.overall_confidence,
            "needs_review": result.needs_review,
        }
    except Exception as exc:
        logger.error(f"Task falhou: {exc}")
        raise self.retry(exc=exc)
