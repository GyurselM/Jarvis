"""
Interfaz base que toda acción ejecutable debe implementar.

Esto es lo que permite que brain/router.py trate a todas las acciones
por igual (abrir una app, controlar Spotify, mandar un correo...) sin
necesitar saber nada de los detalles internos de cada una.
"""

from abc import ABC, abstractmethod
from core.command import Command, CommandResult


class Action(ABC):
    """Contrato que deben cumplir todas las acciones del sistema."""

    @abstractmethod
    def execute(self, command: Command) -> CommandResult:
        """
        Ejecuta la acción con los parámetros del comando recibido.
        Debe devolver siempre un CommandResult, nunca lanzar una
        excepción sin controlar (los errores se capturan aquí dentro
        y se devuelven como CommandResult(success=False, ...)).
        """
        raise NotImplementedError