# from flask_jwt_extended import jwt_required
# from tensorhive.core.services.UsageLoggingService import Summary
# from typing import Dict
# from tensorhive.config import API
# G = API.RESPONSES['general']


# @jwt_required
# def get(id) -> Dict:
#     summary = Summary.find(id)
#     if not summary:
#         return summary, 404
#     return summary, 200
