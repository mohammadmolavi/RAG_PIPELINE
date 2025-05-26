# from transformers import AutoTokenizer, AutoModel
# import os

# model_name = "prithivida/Splade_PP_en_v1"
# save_path = "./models/Splade_PP_en_v1"  

# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModel.from_pretrained(model_name)

# os.makedirs(save_path, exist_ok=True)
# tokenizer.save_pretrained(save_path)
# model.save_pretrained(save_path)

# print(f"Model and tokenizer saved to {save_path}")



from transformers import AutoModel, AutoTokenizer

model_name = "naver/splade-cocondenser-ensembledistil"
save_directory = "./models/splade"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

tokenizer.save_pretrained(save_directory)
model.save_pretrained(save_directory)