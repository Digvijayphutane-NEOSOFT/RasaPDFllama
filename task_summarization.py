from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from PyPDF2 import PdfReader
from langchain.prompts import PromptTemplate
from langchain.chains import StuffDocumentsChain
from langchain.chains.llm import LLMChain

llm = ChatGoogleGenerativeAI(model="gemini-pro")
prompt_template = """Write a concise one-line summary of most recent trnsaction from following:
{summary}
CONCISE SUMMARY: """
prompt = PromptTemplate(
    input_variables=["adjective"], template=prompt_template
)
llm = ChatGoogleGenerativeAI(model="gemini-pro")
chain = prompt | llm | StrOutputParser()
TEXT = """Bank Transaction Report Transaction Number: 1 Date: 2024-06-20 Amount Change: 5000.00 Balance After: 5000.00 Receiver: Bob Information: Initial balance for Bob's account Transaction Number: 2 Date: 2024-06-24 Amount Change: -100.00 Balance After: 4900.00 Receiver: Alice Information: Bank transfer to Alice Transaction Number: 3 Date: 2024-06-24 Amount Change: -100.00 Balance After: 4800.00 Receiver: Alice Information: Bank transfer to Alice Transaction Number: 4 Date: 2024-06-24 Amount Change: -200.00 Balance After: 4600.00 Receiver: Alice Information: Bank transfer to Alice Transaction Number: 5 Date: 2024-06-24 Amount Change: -600.00 Balance After: 4000.00 Receiver: Alice Information: Bank transfer to Alice Transaction Number: 6 Date: 2024-06-24 Amount Change: -100.00 Balance After: 3900.00 Receiver: Alice Information: Bank transfer to Alice Transaction Number: 7 Date: 2024-06-25 Amount Change: -100.00 Balance After: 3800.00 Receiver: Alice Information: Bank transfer to Alice Transaction Number: 8 Date: 2024-06-25 Amount Change: -100.00 Balance After: 3700.00 Receiver: Alice Information: Bank transfer to Alice Transaction Number: 9 Date: 2024-06-25 Amount Change: -100.00 Balance After: 3600.00 Receiver: Alice Information: Bank transfer to Alice Transaction Number: 10 Date: 2024-06-25 Amount Change: -100.00 Balance After: 3500.00 Receiver: Alice Information: Bank transfer to Alice Transaction Number: 11 Date: 2024-06-25 Amount Change: -100.00 Balance After: 3400.00 Receiver: Alice Information: Bank transfer to Alice Transaction Number: 12 Date: 2024-06-25 Amount Change: -200.00 Balance After: 3200.00 Receiver: Alice Information: Bank transfer to Alice Transaction Number: 13 Date: 2024-06-25 Amount Change: -100.00 Balance After: 3100.00 Receiver: Alice"""
response = chain.invoke(TEXT)
print(response)