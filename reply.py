import openai
from api_openai import get_chat_completion
from chroma import collection
from make_embeddings import Article, Section, session_scope
import argparse


def answer(customer_question):
    # take the customer's question and search the most relevant embeddings
    search_results = collection.query(query_texts=[customer_question], n_results=10)
    with session_scope() as db_session:
        sections = (
            db_session.query(Section)
            .filter(Section.checksum.in_(search_results["ids"][0]))
            .all()
        )
        context_sections = "/n---/n".join([section.content for section in sections])

    # construct the prompt
    system_prompt = "You are a friendly and helpful LeagueLobster representative. Given the following sections from LeagueLobster help center articles, try to generate a helpful response to the customer support chat given below using the information from those help article sections, formatted in simple HTML and including links to the relevant article. You may enhance the text within the HTML to make the conversation flow more naturally and feel more friendly. However, if you are unsure and the answer is not explicitly written in the documentation simply reply 'PASS' and the conversation will be looked at by a human. If the user just said hi or stated that they have a question, please prompt them to state their question.\n\nHelp article sections:\n\n"

    prompt = (
        system_prompt
        + context_sections
        + "\nCustomer chat:\n"
        + customer_question
        + "\n---\nAnswer as HTML:\n\n"
    )
    messages = [{"role": "user", "content": prompt}]
    print(prompt)

    # generate the reply
    return get_chat_completion(messages)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Answer customer questions.")
    parser.add_argument("question", help="The customer question to be answered.")
    try:
        args = parser.parse_args()
        answer(args.question)
    except SystemExit:
        answer("how can i enter scores?")