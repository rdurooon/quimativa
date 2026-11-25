"""Minijogo 4 — Análise molecular.

Usa a mesma estrutura de resposta da Identificação, mantendo um schema próprio
para que a identidade do minijogo continue explícita no dispatcher.
"""
from backend.questoes.schemas.identificacao import IdentificationPayload


class MolecularAnalysisPayload(IdentificationPayload):
    """Payload de análise com o mesmo formato validado de identificação."""
