import config
import torch
import pandas as pd
import numpy as np


def process_data(tweet, selected_text, sentiment, tokenizer, max_len):   
    #在字符串头部加入空格 
        tweet = " "+" ".join(str(tweet).split())
        selected_text =" " + " ".join(str(selected_text).split())
        #从text中找出selected_text的起始和终止
        len_st = len(selected_text)-1
        idx0 = -1
        idx1 = -1
        for ind in (i for i, e in enumerate(tweet) if e == selected_text[1]):
            if " " + tweet[ind: ind+len_st] == selected_text:
              idx0 = ind
              idx1 = ind + len_st-1
              break
    #将selected_text的位置在原文中标记出来，并且不包括空格
        char_targets = [0] * len(tweet)
        if idx0 != -1 and idx1 != -1:
            for ct in range(idx0, idx1+1):
                    char_targets[ct] = 1
    #利用Roberta对文本进行编码,token是编码后的文本，ids是编码对应的id，offset是字符在原文本中的起始位置与终止位置
        tok_tweet = tokenizer.encode(tweet)
        tok_tweet_tokens=tok_tweet.tokens
        tok_tweet_ids = tok_tweet.ids
        tok_tweet_offsets = tok_tweet.offsets[1:-1]
    
        targets_idx = []
        for j, (offset1, offset2) in enumerate(tok_tweet_offsets):
            if sum(char_targets[offset1: offset2]) > 0:
                targets_idx.append(j)
    #得出文本的起始和终止
        targets_start = targets_idx[0]
        targets_end = targets_idx[-1]
    #为每种情绪标记对应的id
        sentiment_id = {
        'positive': 3893,
        'negative': 4997,
        'neutral': 8699
        }
    #将文本转换为Roberta模型的输入格式: <s>sentiment</s></s>text</s> 
        input_ids = [0] + [sentiment_id[sentiment]] + [2]+[2] +  tok_tweet_ids + [2]
        token_type_ids = [0, 0, 0,0] + [0] * (len( tok_tweet_ids) + 1)
        mask = [1] * len(token_type_ids)
        tweet_offsets = [(0, 0)] * 4 + tweet_offsets + [(0, 0)]
        targets_start +=4 
        targets_end += 4

      
    #需要padding填充的部分
        padding_length = max_len - len( tok_tweet_ids)
        if padding_length > 0:
            input_ids = input_ids + ([1] * padding_length)
            mask = mask + ([0] * padding_length)
            token_type_ids = token_type_ids + ([0] * padding_length)
            tweet_offsets = tweet_offsets + ([(0, 0)] * padding_length)
    
        return {
        'ids': input_ids,
        'mask': mask,
        'token_type_ids': token_type_ids,
        'targets_start': targets_start,
        'targets_end': targets_end,
        'orig_tweet': tweet,
        'orig_selected': selected_text,
        'sentiment': sentiment,
        'offsets': tweet_offsets
    }


class TweetDataset:
    def __init__(self, tweet, sentiment, selected_text):#每次读入一条数据
        self.tweet = tweet
        self.sentiment = sentiment
        self.selected_text = selected_text
        self.tokenizer = config.TOKENIZER#定义好的Roberta模型的参数
        self.max_len = config.MAX_LEN
    
    def __len__(self):
        return len(self.tweet)

    def __getitem__(self, item):#将输入转换为模型data的一个输入
        data = process_data(
            self.tweet[item],  
            self.selected_text[item], 
            self.sentiment[item],
            self.tokenizer,
            self.max_len
        )
        
        return {
            'ids': torch.tensor(data["ids"], dtype=torch.long),
            'mask': torch.tensor(data["mask"], dtype=torch.long),
            'token_type_ids': torch.tensor(data["token_type_ids"], dtype=torch.long),
            'targets_start': torch.tensor(data["targets_start"], dtype=torch.long),
            'targets_end': torch.tensor(data["targets_end"], dtype=torch.long),
            'orig_tweet': data["orig_tweet"],
            'orig_selected': data["orig_selected"],
            'sentiment': data["sentiment"],
            'offsets_start': torch.tensor([x for x, _ in data["offsets"]], dtype=torch.long),
            'offsets_end': torch.tensor([x for _, x in data["offsets"]], dtype=torch.long)
        }


if __name__ == "__main__":
    df = pd.read_csv(config.TRAINING_FILE)
    df = df.dropna().reset_index(drop=True)
    dset = TweetDataset(tweet=df.text.values, sentiment=df.sentiment.values, selected_text=df.selected_text.values)
    print(dset[100])
    #for j in range(len(dset)):
    #    print(j)
    #    print(dset[j])