# caption_builder.py
from sheet_reader import clean_tag

def build_caption(job_title, top_hashtag, tag_string):
    clean_hashtag = top_hashtag.lstrip("#")
    tags = []

    for raw in tag_string.replace(",", " ").split():
        t = clean_tag(raw)
        if t:
            tags.append(t)

    # debug xem từng tag
    for raw in tag_string.replace(",", " ").split():
        print("RAW:", repr(raw), "=>", repr(clean_tag(raw)))

    tag_lines = "\n".join(tags)

    caption = f"""#{clean_hashtag} #ustariffs
{job_title} with USD $900Trillion+ added value from Option Leadership

Let’s transform your {job_title} to your equity by leveraging tokenization + cross-border payment + climate change Compound Options to accelerate your startup’s growth.

With a funding cost of 15+% for amounts under USD $10Billion (minimum USD $1 Million), we provide a highly efficient way to secure venture capital while maximizing scalability.

With not only your funding target but also your ANY targets, the SIGNIFICANTLY efficient way is donating to TAHK #Foundation for enjoying USD $900+ trillion option leadership then we will help you:
- Donating $150 thousand USD per year service.
- Email to: donate@tahkfoundation.org for your #donation.

As an Universal Interacting & Media Solutions nonprofit, TAHK Foundation will help you interact with the best options for your requirements.

Best regards
{tag_lines}

#Trump #Taxation #BeverlyHills"""
    return caption
