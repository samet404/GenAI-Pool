from typing import Dict, Literal, TypedDict, cast

GoogleModel = Literal[
    'gemma-3-1b-it', 'gemma-3-27b-it', 'gemma-3-4b-it', 'gemma-3-12b-it', 'gemma-3n-e4b-it',
    'gemini-2.0-flash', 'gemini-2.5-flash',  'gemini-2.0-flash-lite', 'gemini-2.5-pro-preview-06-05', 'gemini-1.5-pro'
]

class QuotaLimits(TypedDict, total=False):
    RPM: int # Requests per minute
    TPM: int # Tokens per minute
    RPD: int # Requests per day

GENAI_QUOTAS = cast(Dict[GoogleModel, QuotaLimits], {
    "gemma-3-1b-it": {
        "RPM": 30,
        "TPM": 15000,
        "RPD": 14400,
    },
    'gemma-3-27b-it': {
        "RPM": 30,
        "TPM": 15000,
        "RPD": 14400,
    },
    'gemma-3-4b-it':{
        "RPM": 30,
        "TPM": 15000,
        "RPD": 14400,
    },
    'gemma-3-12b-it': {
        "RPM": 30,
        "TPM": 15000,
        "RPD": 14400,
    },
    'gemma-3n-e4b-it': {
        "RPM": 30,
        "TPM": 15000,
        "RPD": 14400,
    },
    'gemini-2.0-flash': {
        "RPM": 15,
        "TPM": 1000000,
        "RPD": 200,
    },
    'gemini-2.0-flash-lite': {
        "RPM": 30,
        "TPM": 1000000,
        "RPD": 200,
    },
    'gemini-2.5-flash': {
        "RPM": 10,
        "TPM": 1000000,
        "RPD": 200,
    }
})

