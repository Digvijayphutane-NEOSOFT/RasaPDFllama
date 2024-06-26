import os
import pymysql
from datetime import datetime
from typing import Any, Text, Dict, List
from actions.sqltopdf import save_transaction_to_pdf
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, FollowupAction
from rasa_sdk.executor import CollectingDispatcher
import fitz  
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from packaging_legacy.version import parse, LegacyVersion
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from PyPDF2 import PdfReader
from langchain.prompts import PromptTemplate
from langchain.chains import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class ActionConfirmTransfer(Action):
    def name(self) -> Text:
        return "action_confirm_transfer"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ) -> List[Dict]:

        amount = tracker.get_slot("amount")
        recipient = tracker.get_slot("recipient")

        confirm_message = f"Please confirm: Transfer {amount} to {recipient}"
        buttons = [{"title": "Yes", "payload": "/confirm_yes"}, {"title": "No", "payload": "/confirm_no"}]
        dispatcher.utter_message(text=confirm_message, buttons=buttons)

        return []
    
class ActionHandleBankTransfer(Action):
    def name(self) -> Text:
        return "action_handle_bank_transfer"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        
        amount = float(tracker.get_slot("amount"))
        recipient = tracker.get_slot("recipient")
        config = {
            'user': 'root',
            'password': 'password',
            'host': 'localhost',
            'database': 'bank',
            'port': 3306
        }
        
        connection = pymysql.connect(**config)
        cursor = connection.cursor()

        try:
            
            cursor.execute(
                "UPDATE Accounts SET AccountBalance = AccountBalance - %s WHERE AccountName = 'Bob'",
                (amount,)
            )

            # Update recipient's account balance (Alice)
            cursor.execute(
                "UPDATE Accounts SET AccountBalance = AccountBalance + %s WHERE AccountName = %s",
                (amount, recipient)
            )

            # Get the new balance of Bob's account for the transaction record
            cursor.execute("SELECT AccountBalance FROM Accounts WHERE AccountName = 'Bob'")
            new_balance = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM Transactions")
            number_of_transactions = cursor.fetchone()[0]

            # Insert a new transaction
            transaction_number = number_of_transactions + 1
            cursor.execute(
                "INSERT INTO Transactions (Transaction_number, Date, Amount_change, Balance_after, Receiver, Information) VALUES (%s, %s, %s, %s, %s, %s)",
                (transaction_number, datetime.today().strftime('%Y-%m-%d'), -amount, new_balance, recipient, f"Bank transfer to {recipient}")
            )

            # Commit the changes
            connection.commit()

            dispatcher.utter_message(text="Money transfer succeeded! Your new account balance is "+ str(new_balance)+", Is there anything else I can assist you with?" )
            save_transaction_to_pdf(cursor, amount, recipient)
            return [SlotSet("transaction_saved", True)]

        except pymysql.Error as err:
            # Handle errors and rollback changes
            connection.rollback()
            dispatcher.utter_message(text="An error occurred: {}".format(err))
            # You might want to log this error.

        finally:
            # Close the connection
            cursor.close()
            connection.close()

        return []

class ActionGenerateSummary(Action):
    def name(self) -> Text:
        return "action_generate_summary"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Get the path to the PDF file
        pdf_path = 'bank_transaction_report.pdf' # or tracker.get_slot("pdf_path")

        try:
            # Read the PDF file
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()

            # Create a parser
            parser = PlaintextParser.from_string(text, Tokenizer("english"))
            

            # Create an LSA summarizer
            summarizer = LsaSummarizer()
            TEXT = summarizer(parser.document, 1)  # Generate 1-sentence summary
            ##LLM
            llm = ChatGoogleGenerativeAI(model="gemini-pro")

            prompt_template = """Write a concise one-line summary of most recent trnsaction from following:
            {summary}
            CONCISE SUMMARY: """

            prompt = PromptTemplate(
                input_variables=["adjective"], template=prompt_template
            )

            llm = ChatGoogleGenerativeAI(model="gemini-pro")

            chain = prompt | llm | StrOutputParser()

            summary = chain.invoke(TEXT)
            ##/LLM

            # Send the summary to the user
            if summary:
                dispatcher.utter_message(text=f"Summary of last Transaction:\n{summary}")
            else:
                dispatcher.utter_message(text="No summary could be generated.")

        except Exception as e:
            dispatcher.utter_message(text=f"An error occurred: {str(e)}")

        return []