import openai
import streamlit as st
from streamlit_chat import message
import PyPDF2

st.set_page_config(page_title="PDF Text Extractor and GPT-3 Q&A", page_icon=":robot_face:")
st.markdown("<h1 style='text-align: center;'>PDF Text Extractor and GPT-3 Q&A</h1>", unsafe_allow_html=True)

# Initialise session state variables
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []
if 'messages' not in st.session_state:
    st.session_state['messages'] = [
        {"role": "system", "content": "Your name is ResearchPaperGPT and your goal is to help the user understand the research paper that is inputted. "},
    ]   
if 'model_name' not in st.session_state:
    st.session_state['model_name'] = []
if 'cost' not in st.session_state:
    st.session_state['cost'] = []
if 'total_tokens' not in st.session_state:
    st.session_state['total_tokens'] = []
if 'total_cost' not in st.session_state:
    st.session_state['total_cost'] = 0.0



# Upload file
uploaded_file = st.file_uploader("Upload PDF file", type=["pdf"])
if uploaded_file is not None:
    pdf_reader = PyPDF2.PdfReader(uploaded_file)

    # Read in each page of the PDF and store the text in a list
    pages = []
    # Read in each page of the PDF and store the text in the messages list
    for page in pdf_reader.pages:
        text = page.extract_text()
        if text:
            st.session_state['messages'].append({"role": "system", "content": text})




api_key = st.sidebar.text_input('Enter your OpenAI API key')

# Set org ID and API key
#openai.organization = "<YOUR_OPENAI_ORG_ID>"
openai.api_key = api_key


# Sidebar - let user choose model, show total cost of current conversation, and let user clear the current conversation
st.sidebar.title("Sidebar")
model_name = st.sidebar.radio("Choose a model:", ("GPT-3.5", "GPT-4"))
counter_placeholder = st.sidebar.empty()
counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")
clear_button = st.sidebar.button("Clear Conversation", key="clear")


# Map model names to OpenAI model IDs
if model_name == "GPT-3.5":
    model = "gpt-3.5-turbo"
else:
    model = "gpt-4"



# Set maximum context length for the OpenAI model
MAX_CONTEXT_LENGTH = 3900
max_tokens = 3900


import PyPDF2



# reset everything
if clear_button:
    st.session_state['generated'] = []
    st.session_state['past'] = []
    st.session_state['messages'] = [
        {"role": "system", "content": "Your name is ResearchPaperGPT and your goal is to help the user understand the research paper that is inputted. The first set of inputs are going to have the following data structure. each page of a .pdf is going to br given at once. memorize this information and prepare yourself to answer questions from a user. Once all of the pieces of the pdf. are given. You are going to print a few paragraphs. The title of the paper, The authors of the paper, the summarized abstraction of the paper. And a small summary of every page of the paper. Then ask the user if they have any additional questions."}
    ]    
    st.session_state['number_tokens'] = []
    st.session_state['model_name'] = []
    st.session_state['cost'] = []
    st.session_state['total_cost'] = 0.0
    st.session_state['total_tokens'] = []
    counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")


# generate a response
def generate_response(prompt):
    st.session_state['messages'].append({"role": "user", "content": prompt})

    completion = openai.ChatCompletion.create(
        model=model,
        messages=st.session_state['messages']
    )
    response = completion.choices[0].message.content
    st.session_state['messages'].append({"role": "assistant", "content": response})

    # print(st.session_state['messages'])
    total_tokens = completion.usage.total_tokens
    prompt_tokens = completion.usage.prompt_tokens
    completion_tokens = completion.usage.completion_tokens
    return response, total_tokens, prompt_tokens, completion_tokens

# def generate_summary_response(prompt):
#     st.session_state['messages'].append({"role": "user", "content": prompt})

#     completion = openai.ChatCompletion.create(
#         model=model,
#         messages=st.session_state['messages']
#     )
#     response = completion.choices[0].message.content
#     st.session_state['messages'].append({"role": "assistant", "content": response})

#     # print(st.session_state['messages'])
#     total_tokens = completion.usage.total_tokens
#     prompt_tokens = completion.usage.prompt_tokens
#     completion_tokens = completion.usage.completion_tokens
#     return response, total_tokens, prompt_tokens, completion_tokens


# container for chat history
response_container = st.container()
# container for text box
container = st.container()

# uploaded_file = st.file_uploader("Upload PDF file", type=["pdf"])
# if uploaded_file is not None:
#     pdf_reader = PyPDF2.PdfReader(uploaded_file)

#     # Read in each page of the PDF and store the text in a list
#     pages = []
#     page_count = len(pdf_reader.pages)
#     page_limit = 1  # set a limit on the number of pages to process at once

#     for i in range(0, page_count, page_limit):
#         pages = []
#         # Read in each page of the PDF and store the text in the messages list
#         for page in pdf_reader.pages[i:i+page_limit]:
#             text = page.extract_text()

#             generate_summary_response(text)

#             response = completion.choices[0].text
#             st.session_state['messages'].append({"role": "system", "content": response})

#             if text:
#                 pages.append(text)

#             generate_response(text)

           

#         # send the pages to the OpenAI API

#         response = completion.choices[0].text
#         st.session_state['messages'].append({"role": "assistant", "content": response})


with container:
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_area("You:", key='input', height=100)
        submit_button = st.form_submit_button(label='Send')

    if submit_button and user_input:
        output, total_tokens, prompt_tokens, completion_tokens = generate_response(user_input)
        st.session_state['past'].append(user_input)
        st.session_state['generated'].append(output)
        st.session_state['model_name'].append(model_name)
        st.session_state['total_tokens'].append(total_tokens)

        # from https://openai.com/pricing#language-models
        if model_name == "GPT-3.5":
            cost = total_tokens * 0.002 / 1000
        else:
            cost = (prompt_tokens * 0.03 + completion_tokens * 0.06) / 1000

        st.session_state['cost'].append(cost)
        st.session_state['total_cost'] += cost

if st.session_state['generated']:
    with response_container:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state["past"][i], is_user=True, key=str(i) + '_user')
            message(st.session_state["generated"][i], key=str(i))
            st.write(
                f"Model used: {st.session_state['model_name'][i]}; Number of tokens: {st.session_state['total_tokens'][i]}; Cost: ${st.session_state['cost'][i]:.5f}")
            counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")