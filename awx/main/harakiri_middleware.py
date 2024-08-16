import traceback
import logging
import uuid

logger = logging.getLogger('awx.main.middleware')


class HarakiriLoggerMiddleware:
    transactions = {}

    @classmethod
    def handle_signal(cls, *args):
        for t_id, request in HarakiriLoggerMiddleware.transactions.items():
            logger.error(f"Catching harakiri graceful signal for {t_id} with method: {request.method} path: {request.path}")
            logger.error(f"Received harakiri graceful signal while in stack: {''.join(traceback.format_stack()[-5:])}")

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        t_id = str(uuid.uuid4())
        if "X-REQUEST-ID" in request.headers:
            t_id = request.headers["X-REQUEST-ID"]
        HarakiriLoggerMiddleware.transactions[t_id] = request
        try:
            return self.get_response(request)
        finally:
            HarakiriLoggerMiddleware.transactions.pop(t_id)
