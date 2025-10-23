import streamlit as st
import time

def show_marquee():
    """Dummy marquee (teks berjalan) untuk pengujian."""
    st.markdown(
        """
        <style>
        .marquee {
            width: 100%;
            overflow: hidden;
            white-space: nowrap;
            box-sizing: border-box;
            animation: marquee 15s linear infinite;
            font-weight: bold;
            color: #ff4b4b;
            background-color: #fff5f5;
            border-radius: 8px;
            padding: 8px;
            font-size: 1rem;
        }
        @keyframes marquee {
            0%   { text-indent: 100% }
            100% { text-indent: -100% }
        }
        </style>
        <div class="marquee">🚧 Dummy Notice: This is a testing marquee banner — not for production 🚧</div>
        """,
        unsafe_allow_html=True
    )

# Uncomment baris di bawah jika ingin test langsung file ini
# if __name__ == "__main__":
#     st.set_page_config(page_title="Marquee Dummy Test")
#     show_marquee()
#     time.sleep(10)
