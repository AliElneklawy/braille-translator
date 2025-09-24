from transformers import T5ForConditionalGeneration, AutoTokenizer


class TextCorrection:
    def __init__(self) -> None:
        self.path_to_model = "ai-forever/T5-large-spell"
        self.model = T5ForConditionalGeneration.from_pretrained(self.path_to_model)
        self.tokenizer = AutoTokenizer.from_pretrained(self.path_to_model)
        self.prefix = "spelling correction: "

    def correction(self, uncorrected_text):
        self.sentence = self.prefix + uncorrected_text
        self.input_ids = self.tokenizer.encode(self.sentence, return_tensors="pt")
        self.output_ids = self.model.generate(self.input_ids, max_length=512)
        corrected_text = self.tokenizer.decode(
            self.output_ids[0], skip_special_tokens=True
        )

        return corrected_text
