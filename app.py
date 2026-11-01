
import os

import pandas as pd
import plotly.express as px
import streamlit as st

from labeler import label_comment

TITLE = "The Corner Table"
QUESTION = "Which part of the dining experience should we fix first to raise customer ratings?"
LOW_RATING, HIGH_RATING = 2,4
CSV_FILE = "feedback.csv"
COLORS = {"food": "#2BB38A", "service": "#3A7BD5", "value": "#E8A317",
          "atmosphere": "#9B59B6", "unclear": "#D0D0D0"}
LOGO = "logo.png"
st.set_page_config(page_title=TITLE, page_icon=LOGO, layout="wide")
st.image(LOGO, width=90)
st.title(TITLE)
st.caption("Customers leave feedback. The app labels it and saves it. The owner analyzes it later.")

# Load the saved feedback, or start with an empty table
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
else:
    df = pd.DataFrame(columns=["comment", "rating", "label", "tone"])

tab_customer, tab_owner = st.tabs(["Customer: leave feedback", "Owner: analyze the feedback"])

# ---- Customer tab: type feedback, pick stars, get a label, save --------------
with tab_customer:
    st.subheader("Tell us about your visit")
    with st.form("feedback_form", clear_on_submit=True):
        stars = st.feedback("stars")          # nothing until clicked, then 0 to 4
        comment = st.text_area("Your comment (optional)")
        submitted = st.form_submit_button("Send feedback")

    if submitted:
        comment = comment.strip()
        if not comment and stars is None:
            st.error("Please choose a star rating, write a comment, or both.")
        else:
            if comment: label,tone = label_comment(comment)
            else: label,tone = "no comment","no comment"
            rating = stars + 1 if stars is not None else None
            new_row = pd.DataFrame([{"comment": comment.strip(), "rating": rating, "label": label, "tone": tone}])
            pd.concat([df, new_row], ignore_index=True).to_csv(CSV_FILE, index=False)
            df = pd.read_csv(CSV_FILE)
            st.success("Thank you for your feedback!")
            if comment:
              st.caption(f"Behind the scenes, the app labeled it: {label} ({tone})")

# ---- Owner tab: analyze the feedback ----------------------------------------
with tab_owner:
    st.subheader(QUESTION)
    if df.empty:
        st.info("No feedback yet. Switch to the customer tab and add the first comment.")
    else:
        comments = df[df["label"] != "no comment"]
        # Comments to read carefully: the label and the rating disagree, or the label is unclear
        review = ((comments["tone"] == "positive") & (comments["rating"] <= LOW_RATING)) \
             | ((comments["tone"] == "negative") & (comments["rating"] >= HIGH_RATING)) \
             | (comments["label"] == "unclear")
        to_review = comments[review]

        m1, m2, m3 = st.columns(3)
        m1.metric("Feedback Received", len(df))
        m2.metric("Average Stars", f"{df['rating'].mean():.1f}" if df["rating"].notna().any() else "No ratings yet")
        m3.metric("Need manual review", len(to_review))


        col1, col2 = st.columns(2)

        with col1:
            st.caption("Average stars by label (lowest = fix first)")
            rated = comments[(comments["label"] != "unclear") & comments["rating"].notna()]
            avg = rated.groupby("label")["rating"].mean().round(1).sort_values().reset_index()
            fig = px.bar(avg, x="label", y="rating", color="label", text="rating",
                         color_discrete_map=COLORS, range_y=[0,5])
            fig.update_layout(showlegend=False, xaxis_title=None, yaxis_title="Average Stars")
            st.plotly_chart(fig, width="stretch")

        with col2:
            st.caption("Number of comments by label")
            counts = comments["label"].value_counts().rename_axis("label").reset_index(name="count")
            fig = px.bar(counts, x="label", y="count", color="label", text="count",
                         color_discrete_map=COLORS)
            fig.update_layout(showlegend=False, xaxis_title=None, yaxis_title="Comments")
            st.plotly_chart(fig, width="stretch")

        st.subheader("Comments that need manual review")
        st.caption("The label is unclear, or the tone and the star rating disagree.")
        if to_review.empty:
          st.write("Nothing to review right now.")
        for _, row in to_review.iterrows():
          stars_text = f"{int(row['rating'])} star(s)" if pd.notna(row['rating']) else "No rating"
          st.markdown(f"**{row['label']} | {row['tone']} | {stars_text}**")
          st.write(row['comment'])
          st.divider()

        with st.expander("All feedback"):
            st.dataframe(df, hide_index=True, width="stretch")
        st.download_button("Download CSV", df.to_csv(index=False), file_name="feedback.csv")
        st.caption("On the free Streamlit Cloud, the saved file can disappear when the app restarts. "
                   "Download your CSV to keep it.")
