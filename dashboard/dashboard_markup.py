import streamlit as st

# Custom HTML for the landing page layout
st.markdown("""
    <style>
        /* Style for top bar */
        .top-bar {
            display: flex;
            justify-content: space-between;
            padding: 10px;
            background-color: #1e3d58;
            color: white;
            font-size: 20px;
        }
        
        .top-bar .login-register {
            font-size: 18px;
        }

        /* Style for the menu bar */
        .menu-bar {
            width: 200px;
            position: fixed;
            top: 50px;
            left: 0;
            bottom: 0;
            background-color: #f1f1f1;
            padding: 20px;
            font-size: 18px;
        }
        
        /* Main content styling */
        .main-content {
            margin-left: 220px;
            padding: 20px;
        }

        .button {
            background-color: #4CAF50; /* Green */
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
        }
        
        .button:hover {
            background-color: #45a049;
        }

    </style>
""", unsafe_allow_html=True)

# Top Bar with Login and Register buttons
st.markdown('<div class="top-bar">Landing Page <div class="login-register"><button class="button" onclick="window.location.href=\'#login\'">Login</button> <button class="button" onclick="window.location.href=\'#register\'">Register</button></div></div>', unsafe_allow_html=True)

# Left-side Menu Bar
st.markdown('<div class="menu-bar">Menu <ul><li>Option 1</li><li>Option 2</li><li>Option 3</li></ul></div>', unsafe_allow_html=True)

# Main Content Area
st.markdown('<div class="main-content">Welcome to the Landing Page! <br><br> Use the buttons above to log in or register.</div>', unsafe_allow_html=True)

