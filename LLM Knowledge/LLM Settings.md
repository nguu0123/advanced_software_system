## Temperature 
- The lower the temperature, the more deterministic the results 
- Increasing temperature means more randomness where you increase the weights of the other possible tokens
## Top P 
- A sampling technique with temperature, called nucleus sampling, where you can control how deterministic the model is 
- Low `top_p` means less token is consider
- High `top_p` means more token is consider, meaning more diverse outputs
  
> [!NOTE] General recommendation 
>  Alter temperature or Top P but not both
## Max Length 
- Number of tokens that the model generates 
## Frequency penalty 
- `frequency_penalty` applies penalty on the next token proportional to how many times that token already appeared in the response and prompt 
- Higher `frequency_penalty`, the less likely a word will appear again
## Presence penalty 
- The `presence_penalty` applies a penalty on repeated token 
- The token that appears twice and a token that appears 10 times are *penalized* the same 

> [!NOTE] General recommendation 
>  Alter frequency or presence penalty but not both