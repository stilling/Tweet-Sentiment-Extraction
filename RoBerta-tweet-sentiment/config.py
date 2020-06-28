import tokenizers
import os
MAX_LEN = 160
TRAIN_BATCH_SIZE = 32
VALID_BATCH_SIZE = 16
EPOCHS = 15
BERT_PATH = "../input/roberta-base/"
MODEL_PATH = "model.bin"
TRAINING_FILE = "../input/tweet-sentiment-extraction/train.csv"
TOKENIZER = tokenizers.ByteLevelBPETokenizer(
            vocab_file='../input/roberta-base/vocab.json', 
            merges_file='../input/roberta-base/merges.txt', 
            lowercase=True,
            add_prefix_space=True
)
