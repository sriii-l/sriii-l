import requests
import streamlit as st
from streamlit_option_menu import option_menu
import pymongo
from streamlit_lottie import st_lottie

# Access MongoDB URI from Streamlit secrets
mongo_uri = st.secrets["MONGO_URI"]["uri"]

# Initialize MongoDB client
client = pymongo.MongoClient(mongo_uri)
db = client["project"]
collection = db["Donation"]
usercol = db["userdata"]

# Option menu for navigation
selected = option_menu(
    menu_title=None, 
    options=["Home", "Donate Blood", "Need Blood"],
    icons=["house", "heart", ""],
    orientation="horizontal"
)

# Session state for login status
if 'key' not in st.session_state:
    st.session_state['key'] = False

def homie():
    choice = option_menu(menu_title=None, options=["New User", "Existing User", "Log out"])
    st.title("Blood Donation Portal")

    with st.container():
        left_col, right_col = st.columns(2)
        with left_col:
            if choice == "New User":
                st.subheader("New User")
                st.write("Please register to access the Blood Donation Portal.")
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                email = st.text_input("Email")

                if st.button("Register"):
                    if not username or not password or not email:
                        st.error("Please fill in all required fields.")
                    else:
                        existing_user = usercol.find_one({"username": username})
                        if existing_user:
                            st.error("Username is already taken. Please choose a different one.")
                        else:
                            user_data = {
                                "username": username,
                                "password": password,
                                "email": email,
                            }
                            usercol.insert_one(user_data)
                            st.success("Registration successful!")
                            st.write("Go To Login")

            elif choice == "Existing User":
                st.write("Please log in to access the Blood Donation Portal.")
                with st.form("User Details"):
                    username = st.text_input("Username")
                    password = st.text_input("Password", type="password")

                    if st.form_submit_button("Login"):
                        if not username or not password:
                            st.write("Please fill in all required fields.")
                        else:
                            user = usercol.find_one({"username": username, "password": password})
                            if user:
                                st.success("Login successful!")
                                st.session_state.key = True
                            else:
                                st.error("Invalid username or password. Please try again.")

            elif choice == "Log out":
                if st.session_state.key:     
                    st.success("Successfully Logged out")
                    st.session_state.key = False
                else:
                    st.error("Please Login First")

        with right_col:
            st.markdown(
                '<iframe src="https://lottie.host/?file=dc159f25-5e8c-4a5a-83d3-62fc1e8291c6/fG8aNuB6lA.json" width="500px" height="500px" style="border-radius:50px"></iframe>', 
                unsafe_allow_html=True
            )

def navigate_to_donate():
    if st.session_state.key:
        st.subheader("Donor")
        with st.form("Donor Details"):
            st.write("Please enter your donor details:")
            name = st.text_input("Full Name")
            age = st.number_input("Age", min_value=18, max_value=99, value=18)
            blood_type = st.selectbox("Blood Type", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
            contact = st.text_input("Contact Number")
            location = st.text_input("Location/Address")
            consent = st.checkbox("I consent to donate blood.")

            if st.form_submit_button("Submit"):
                if not name or not contact or not location or not consent:
                    st.error("Please fill in all required fields.")
                else:
                    donor_data = {
                        "name": name,
                        "age": age,
                        "blood_type": blood_type,
                        "contact": contact,
                        "location": location
                    }
                    collection.insert_one(donor_data)  
                    st.success("Donor details submitted successfully.")
    else:
        st.error("Please Register/Login")

def navigate_to_receive():
    if st.session_state.key:
        st.subheader("Receiver")
        with st.form("Receiver Details"):
            st.write("Please enter your receiver details:")
            name = st.text_input("Full Name")
            age = st.number_input("Age", min_value=0, max_value=99, value=18)
            blood_type = st.selectbox("Required Blood Type", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
            contact = st.text_input("Contact Number")
            location = st.text_input("Location/Address")
            urgency = st.radio("Urgency", ["Urgent", "Not Urgent"])
            additional_info = st.text_area("Additional Information")
            consent = st.checkbox("I need blood donation.")

            if st.form_submit_button("Search Donors"):
                if not name or not contact or not location or not urgency or not consent:
                    st.error("Please fill in all required fields.")
                else:
                    query = {"location": location, "blood_type": blood_type}
                    matching_donors = collection.find(query)
                    if matching_donors.count() != 0:
                        st.subheader("Matching Donors")
                        for donor in matching_donors:
                            st.write(f"Name: {donor['name']}")
                            st.write(f"Age: {donor['age']}")
                            st.write(f"Blood Type: {donor['blood_type']}")
                            st.write(f"Contact: {donor['contact']}")
                            st.write(f"Location: {donor['location']}")
                    else:
                        st.markdown("No matching donors found in the database. You can explore other blood donation portals or resources:")
                        st.markdown("[Indian Red Cross Society](https://indianredcross.org/)")
                        st.markdown("[Friends2Support](https://www.friends2support.org/)")
                        st.markdown("[Sankalp India Foundation](http://www.sankalpindia.net/)")
                        st.markdown("[BloodConnect](https://www.bloodconnect.org/)")
    else:
        st.error("Please Register/Login")  

if selected == "Home":
    homie()
elif selected == "Donate Blood":
    navigate_to_donate()
elif selected == "Need Blood":
    navigate_to_receive()
