"""
Orange3 Prompt Widget
=====================

Widget para definir manualmente as orientações que serão
enviadas à LLM durante a conversa no chatbot.
"""

from AnyQt.QtWidgets import QTextEdit

from Orange.widgets import widget, gui, settings
from Orange.widgets.widget import Output


class OWPrompt(widget.OWWidget):
    name = "Prompt"
    description = "Define manual prompt instructions for the LLM"
    icon = "icons/chatbot.svg"
    priority = 85
    keywords = ["prompt", "instruction", "llm", "chatbot"]

    want_main_area = False
    resizing_enabled = False

    layer_name = settings.Setting("Prompt Layer")

    prompt_instruction = settings.Setting(
        "Responda de forma clara e objetiva."
    )

    class Outputs:
        prompt_config = Output("Prompt Config", dict)

    def __init__(self):
        super().__init__()

        self._setup_gui()
        self._update_preview()
        self.commit()

    def _setup_gui(self):
        prompt_box = gui.widgetBox(
            self.controlArea,
            "Prompt Configuration"
        )

        gui.lineEdit(
            prompt_box,
            self,
            "layer_name",
            label="Layer name:",
            callback=self.on_prompt_changed,
        )

        instruction_label = gui.label(
            prompt_box,
            self,
            "Prompt instructions:"
        )
        instruction_label.setWordWrap(True)

        self.prompt_editor = QTextEdit()
        self.prompt_editor.setPlainText(
            self.prompt_instruction
        )
        self.prompt_editor.setMinimumHeight(150)

        prompt_box.layout().addWidget(
            self.prompt_editor
        )

        help_label = gui.label(
            prompt_box,
            self,
            "Digite somente as orientações para a LLM. "
            "A pergunta será escrita posteriormente no Chatbot, "
            "e o contexto será recuperado pelos documentos do RAG."
        )
        help_label.setWordWrap(True)

        preview_box = gui.widgetBox(
            self.controlArea,
            "Preview"
        )

        self.preview_label = gui.label(
            preview_box,
            self,
            ""
        )
        self.preview_label.setWordWrap(True)

        status_box = gui.widgetBox(
            self.controlArea,
            "Status"
        )

        self.status_label = gui.label(
            status_box,
            self,
            "Ready"
        )

        self.prompt_editor.textChanged.connect(
            self.on_prompt_changed
        )

    def on_prompt_changed(self):
        """
        Atualiza a orientação quando o usuário altera
        o nome da camada ou o conteúdo do prompt.
        """

        if hasattr(self, "prompt_editor"):
            self.prompt_instruction = (
                self.prompt_editor.toPlainText()
            )

        self._update_preview()
        self.commit()

    def _update_preview(self):
        """
        Mostra como a orientação participará
        do fluxo final da aplicação.
        """

        instruction = (
            self.prompt_instruction or ""
        ).strip()

        if not instruction:
            self.preview_label.setText(
                "No prompt instruction defined."
            )
            self.status_label.setText(
                "No prompt configured"
            )
            return

        preview = (
            "Orientação enviada à LLM:\n\n"
            f"{instruction}\n\n"
            "Durante a conversa, também serão adicionados:\n"
            "- contexto recuperado pelo RAG;\n"
            "- histórico da conversa;\n"
            "- pergunta escrita no Chatbot."
        )

        self.preview_label.setText(preview)

        self.status_label.setText(
            f"Prompt ready - {len(instruction)} characters"
        )

    def commit(self):
        """
        Envia a configuração manual do prompt
        para o widget LLM.
        """

        instruction = (
            self.prompt_instruction or ""
        ).strip()

        layer_name = (
            self.layer_name or "Prompt Layer"
        ).strip()

        if not instruction:
            self.Outputs.prompt_config.send(None)
            self.info.set_output_summary(
                self.info.NoOutput
            )
            return

        prompt_config = {
            "layer_name": layer_name,
            "prompt_instruction": instruction,

            # Campo adicional para facilitar
            # a integração com o OWLLM.
            "prompt_text": instruction,

            "prompt_enabled": True,
            "prompt_type": "manual",
        }

        self.Outputs.prompt_config.send(
            prompt_config
        )

        self.info.set_output_summary(
            f"{layer_name}: {len(instruction)} characters"
        )


if __name__ == "__main__":
    from Orange.widgets.utils.widgetpreview import WidgetPreview

    WidgetPreview(OWPrompt).run()