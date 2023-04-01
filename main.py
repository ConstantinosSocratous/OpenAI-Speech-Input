from dotenv.main import load_dotenv
import openai
import pyaudio
import wave
import keyboard
import os

load_dotenv()

openai.api_key =  os.getenv('OPENAI_API_KEY')

#########  RECORD AND SAVE AUDIO  #########
AUDIO_FILE_NAME = "output.wav" 
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 0

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("Recording... press Enter to stop")

frames = []

while True:
    if keyboard.is_pressed('\n'): # check if Enter key is pressed
        break
    data = stream.read(CHUNK)
    frames.append(data)

print("Recording stopped")

stream.stop_stream()
stream.close()
p.terminate()

print("Saving temporary file...")

wf = wave.open(AUDIO_FILE_NAME, "wb")
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b"".join(frames))
wf.close()
##################################

########### WHISPER ############
f = open(AUDIO_FILE_NAME, "rb")
print("Transforming audio into text...")
transcript_response = openai.Audio.transcribe("whisper-1", f, language="en")
transcript = transcript_response.text
f.close()

if os.path.exists(AUDIO_FILE_NAME): # delete audio file
    os.remove(AUDIO_FILE_NAME)
##################################

########### ChatGPT ChatCompletion ############

file = open("conv.txt", "r")
current_conv = file.read()
print("ChatGPT 3.5 is answering at your question...")

completion = ""
try:
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": str(current_conv)},
        {"role": "user", "content": str(transcript)}
    ])
except openai.error.InvalidRequestError:
    print("Invalid Request - Not enough tokens left for this converstation. Please start a new conversation")

print("-------------------")
print(completion.usage)

new_question = "- User:\n" + transcript
new_answer = "- ChatGPT:\n" + completion.choices[0].message.content

print(new_question)
print(new_answer)

file = open("conv.txt", "w")
file.write(current_conv)
file.write(new_question)
file.write("\n")
file.write(new_answer)
file.write("\n")
file.write("\n")
file.close()
##################################


############ DALLE 2 ############
# image_resp = openai.Image.create(prompt="two dogs playing chess, oil painting", n=4, size="512x512")
# print(image_resp)

# for index,image in enumerate(image_resp.data):
#     img_data = requests.get(image.url).content
#     name = 'image' + str(index) + '.jpg'
#     with open(name, 'wb') as file:
#         file.write(img_data)
##################################