from transformers import AutoModel, AutoTokenizer

model_name = "naver/splade-cocondenser-ensembledistil"
save_directory = "./models/splade"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

tokenizer.save_pretrained(save_directory)
model.save_pretrained(save_directory)