
from .models import *
from .serializers import *
import uuid


def generate_unique_transaction_id():
    """Generates a unique 12-character transaction ID"""
    while True:
        tx_id = f"tx{uuid.uuid4().hex[:12]}"
        if not Transaction.objects.filter(transaction_id=tx_id).exists():
            break

    return tx_id

def generate_unique_stan():
    """Generates a unique 12-digit System Trace Audit Number (STAN)"""
    while True:
        stan = ''.join(random.choices('0123456789', k=12))
        if not Transaction.objects.filter(stan=stan).exists():
            return stan
        
def generate_unique_rrn():
    """Generates a unique 20-character Retrieval Reference Number (RRN)"""
    while True:
        rrn = uuid.uuid4().hex[:20].upper()
        if not Transaction.objects.filter(rrn=rrn).exists():
            return rrn
