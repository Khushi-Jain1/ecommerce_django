# ecommerce_django

## Step 1: Install OS essentials 

    sudo apt-get update

    sudo apt-get upgrade

## Step 2: Download source code
 
    git clone 

    cd ecommerce_django/

## Step 3: Create virtual environement

    pip install virtualenv

    python3 -m venv .venv

    source .venv/bin/activate

## Step 4: Install all dependencies

    pip install -r requirements.txt

## Step 5: Setup environment variables 

    create .env file inside Ecommerce/

    and add following info to it:

    ``
    email_host = 
    email_host_password = 

    Database_name = 
    Database_user = 
    Database_password = 

    SECRET_KEY = 

    PAYPAL_RECEIVER_EMAIL = 

    MAILCHIMP_API_KEY = 
    MAILCHIMP_DATA_CENTER = 
    MAILCHIMP_EMAIL_LIST_ID = 

    SOCIAL_AUTH_FACEBOOK_KEY = 
    SOCIAL_AUTH_FACEBOOK_SECRET = 

    SOCIAL_AUTH_GITHUB_KEY = 
    SOCIAL_AUTH_GITHUB_SECRET = 

    ``


