def get_marquee_title(title: str) -> str:
    """Mengembalikan judul dashboard dengan teks (Dummy) berjalan modern dan jarak rapi"""
    marquee_html = f"""
    <style>
    @keyframes scroll-text {{
        0% {{ transform: translateX(100%); }}
        100% {{ transform: translateX(-100%); }}
    }}
    </style>

    <div style="
        display: flex;
        align-items: left;
        gap: 0px;
        margin: 0;
        padding: 200;
    ">
        <h1 style="
            font-weight: 700;
            font-size: 3rem;
            margin: 0;
            padding: 0;
            line-height: 1.2;
        ">
            {title}
        </h1>
        <div style="
            overflow: hidden;
            white-space: nowrap;
            width: 100px;
            margin: 0;
            padding: 0;
        ">
            <div style="
                display: inline-block;
                color: orange;
                font-weight: 600;
                font-size: 1.3rem;
                line-height: 1.2;
                animation: scroll-text 6s linear infinite;
            ">
                (Dummy)
            </div>
        </div>
    </div>
    """
    return marquee_html
