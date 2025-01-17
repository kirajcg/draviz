from collections import OrderedDict
from typing import Dict

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from st_btn_select import st_btn_select


def create_plot(answers: Dict[str, int], answer_dict: Dict[int, str]) -> None:
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=[v for k, v in answers.items() if v != 4],
        theta=[k for k, v in answers.items() if v != 4],
        fill="toself",
        # name=phase,
        text=[k for k, v in answers.items() if v != 4],
        hoverinfo="text"
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                tickmode="array",
                tickvals=[0, 1, 2, 3],
                ticktext=list(answer_dict.values()),
                range=[0, 3],
                categoryorder="category ascending"
            ),
            angularaxis=dict(
                direction="clockwise"
            )
        ),
        showlegend=False,
        font=dict(size=12)
    )

    st.plotly_chart(fig)


def print_questions(questions: pd.DataFrame, answer_dict: Dict[int, str]) -> Dict[str, int]:
    answers = OrderedDict()
    for i in range(len(questions)):
        qstring = "%i. %s" % (questions["question_id"][i], questions["question_text"][i])
        qshort = "%i. %s" % (questions["question_id"][i], questions["shorthand"][i])
        ans_val = st.radio(qstring, answer_dict.values())
        answers[qshort] = [k for k, v in answer_dict.items() if v == ans_val][0]
    return answers


def main() -> None:
    langs: Dict[str, str] = {
        'English': 'en',
        'Svenska': 'sv'
    }

    lang_select = st_btn_select(list(langs.keys()))
    language = langs[lang_select]

    dd = OrderedDict()
    if language == "en":
        title = "Data Readiness Assessment"
        dd: Dict[int, str] = {
            0: "Don't know",
            1: "No",
            2: "Partially",
            3: "Yes",
            4: "Not relevant"
        }

        q_options: Dict[int, str] = {
            0: "None",
            1: "Default questions",
            2: "User-specified questions"
        }
        q_prompt = "Select source of questions"
        upload_prompt = "Upload csv file with questions"

    elif language == "sv":
        title = "Bedömning av databeredskap"
        dd: Dict[int, str] = {
            0: "Vet inte",
            1: "Nej",
            2: "Delvis",
            3: "Ja",
            4: "Inte relevant"
        }

        q_options: Dict[int, str] = {
            0: "None",
            1: "Standardfrågor",
            2: "Egna frågor"
        }
        q_prompt = "Välj källa till frågor"
        upload_prompt = "Ladda upp csv-fil med frågor"
    else:
        raise RuntimeError(f"Unknown language: '{language}'")

    st.title(title)
    q_mode = st.selectbox(q_prompt, q_options.values())

    mode = [k for k, v in q_options.items() if v == q_mode][0]

    if mode == 0:
        input_file = None
    elif mode == 1:
        input_file = "data/defaultq_%s.csv" % language
    elif mode == 2:
        input_file = st.file_uploader(upload_prompt, type="csv")

    if input_file is not None:
        qq = pd.read_csv(input_file)
        try:
            answers = print_questions(qq, dd)
            create_plot(answers, dd)
        except KeyError:
            st.write(
                "Not a valid question file. Expected columns question_id, shorthand, question_text. Instead got %s." % ", ".join(
                    qq.columns))


if __name__ == "__main__":
    main()
