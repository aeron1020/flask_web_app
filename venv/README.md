# flask_web_app
# Espasyo
#### Video Demo:  https://youtu.be/p0PxIBDSE0o
#### Description: "Espasyo is a Filipino word that means 'space'. This is a simple publishing platform that serves as a space for writers who want to share their stories, ideas, or thoughts where they can freely express themselves, with the intention of both inspiring others and finding inspiration in return. Espasyo nurtures a collective of individuals who are motivated to forge connections through the influence of words and stories".

## Files and Functionalities
1. ### app.py
The main application where Flask app is defined and configured. It includes routes for different pages and fuctionalities, as well as various utility functions and configurations.

2. ### Python Imports
__flask__: for my framework
flash, redirect, render_template, request, session, url_for, jsonify from flask
__Session from flask_session__: for managing user sessions

__secure_filename from wekzeug.utils__: for securing the filename so it does not contain any malicious character

__pytz__: for formatting time/timezones

__datetime, timedelta from datetime__: for formatting datetime/durations

__check_password_hash, generate_password_hash from werkzeug.security__: for checking and hashing of password securely.

3. ### Some Functions
__time_format()__: for converting timestamp into "x minutes ago" or "days ago" format.
__login_required()__: verifiying the user before allowing to access the certain routes.

4. ### Templates
__layout.html__: provides the consistent structure, header, footer nav bar of the web app
__index("/")__: responsible for displaying the latest articles on the homepage.
__adminresgister("/adminregister")__: allows a writer or administrator to register new accounts. Responsible for validating data, enforces passwords and store account info in the db.
__adminlogin("/adminlogin")__: handling login authentication.
__logout("logout")__: logs the user out and redirects to the homepage.
__blogs("/blogs")__: displays all the blog articles with their metadata.
__create_blog("/create_blog")__: for creating new blog posts. Handles submissions and validation. This page is having a vanilla js functionalies that handles a dynamic addition of content, figure, and description.
__myblogs("/myblogs")__: displays blog articles that created by the writer or logged-in user. this is act like a dashboard of all the articles that writes by the user, having the control for; update and delete.
__update_post("/blogs/update_post/<int:post_id>")__: for updating the content details of their own blog post.
__delete_post("/blogs/delete_post/<int:post_id>")__: for deleting their own blog post. Handles form submission, validates input, and delete post from the db.
__blog_art("/blog_art")__: or blog articles displays the detailed view of a specific blog with all of its content. This is where you read the post.
__settings("/settings")__: for user setting in the future, it only contains the change password.
__changeadminname("changeadminname")__: for changing the username/adminname.
__changepassword("changepassword")__: for changing the users password.
__about("/about")__: a brief about story for this project

4. ### vanila js
for some dynamically design animation located in some html; with style.css

5. ### style.css
__Global styles__: define the three main color of the web app.
__Navbar styles__: includes transistions for smooth animation effects when hovering over links. Adding hide to the navbar when ever scrolling down and display again when scrolling up.
__Alert styles__: I use this for displaying the flash function for alerting the user prior to their finish action.
__Blog styles__: for blog group html, including the contentm title, avatar image, and text. It also includes some animation for fading in content.
__Create blog styles__: including the post container, title, content, buttons, inputs and figures.
__Miscellaneous style__: additional styles for various elements and componets.

6. ### bootstrap
I primarily utilize Bootstrap as a framework to structure key elements of my web applications, including layout design, button styling, form inputs, and navigation bars.

7. ### favicon
For the icon displayed in the browser's tab bar, depicting a "contemplative image".

8. ## olsenaeron.db SQLite database schema
__admin table__: id, adminname, hash and timestamp
__sqlite_sequence table__: for tracking the auto-increment sequence for each data.
__post table__: id, title, post_date, author_id(admin(id))
__head_media table__: id, media_type, media_url, post_id(post(id))
__content table__: id, content, figure_media_type, figure_media_url, figure_description, post_id(post(id))

All in all, the design of this web app draws significant inspiration from news platforms, where the most recent content is prominently displayed at the top. When developing the blog feature, a dynamic approach was implemented to allow writers to seamlessly add content and associated figures. This feature enables authors to enhance their articles with images, allowing readers to visualize concepts more effectively. The concept is reminiscent of the floating images often found on Wikipedia, where images are positioned alongside text to provide context and visualization. This approach aims to create an engaging and informative reading experience for the audience.
In addition to the mentioned features, the web application incorporates a preview function for each uploaded image. This feature enhances the writer's ability to visualize their content during the post creation or updating phase. By offering a preview of how uploaded images will appear alongside the text, writers can ensure that the content and images are harmoniously integrated. This preview mechanism streamlines the content creation process, guaranteeing that the eventual post presentation aligns with the writer's intentions and offers an engaging visual encounter for the readers.