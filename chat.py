import openai
import creds


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


openai.api_key = creds.OPENAI_API_KEY
openai.api_base = 'https://api.openai.com/v1'


def gpt3_completion(messages, engine='gpt-3.5-turbo', temp=0.9, tokens=100, freq_pen=2.0, pres_pen=2.0, stop=['CHATTER:', 'Purr-bot:']):
    try:
        response = openai.ChatCompletion.create(
            model=engine,
            messages=messages,
            temperature=temp,
            max_tokens=tokens,
            frequency_penalty=freq_pen,
            presence_penalty=pres_pen,
            stop=stop)
        text = response['choices'][0]['message']['content'].strip()
        return text
    except Exception as e:
        print(e)
        return ""
    return ""
    
def gpt3_completion_prompt(message, engine='gpt-3.5-turbo-instruct', temp=0.9, tokens=100, freq_pen=2.0, pres_pen=2.0, stop=['CHATTER:', 'Purr-bot:']):
    try:
        #print(message)
        response = openai.Completion.create(
            model=engine,
            prompt=message,
            #messages=prompt,
            temperature=temp,
            max_tokens=tokens,
            frequency_penalty=freq_pen,
            presence_penalty=pres_pen,
            stop=stop)
            
        #print(response)
        text = response['choices'][0]['text'].strip()
        return text
    except Exception as e:
        print(e)
        return ""
    return ""