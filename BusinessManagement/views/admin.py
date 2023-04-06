import io
from flask import Blueprint, render_template, request, redirect, flash
from werkzeug.utils import secure_filename
from sql.db import DB
import traceback
admin = Blueprint('admin', __name__, url_prefix='/admin')
import csv

@admin.route("/import", methods=["GET","POST"])
def importCSV():
    if request.method == "POST":
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file', "warning")
            return redirect(request.url)
        # TODO importcsv-1 check that it's a .csv file, return a proper flash message if it's not
        # Gagan Indukala Krishna Murthy - gi36 - 6th April
        # Checking if the file ends with .csv and returning a flash message, if the format is not proper.
        # using endswith() method to check the format. 
        if file and secure_filename(file.filename):
            if not file.filename.endswith(".csv"):
                flash("Please check the format of the file, only csv file format is accepted","danger")
                return redirect(request.url)
            companies = []
            employees = []
            # DON'T EDIT
            company_query = """
            INSERT INTO IS601_MP3_Companies (name, address, city, country, state, zip, website)
                        VALUES (%(name)s, %(address)s, %(city)s, %(country)s, %(state)s, %(zip)s, %(website)s)
                        ON DUPLICATE KEY UPDATE 
                        address=values(address),
                        city=values(city),
                        country=values(country),
                        state=values(state),
                        zip=values(zip),
                        website=values(website)
            """
            # DON'T EDIT
            employee_query = """
                        INSERT INTO IS601_MP3_Employees (first_name, last_name, email, company_id)
                        VALUES (%(first_name)s, %(last_name)s, %(email)s, (SELECT id FROM IS601_MP3_Companies WHERE name = %(company_name)s LIMIT 1))
                        ON DUPLICATE KEY UPDATE first_name=%(first_name)s, 
                        last_name = %(last_name)s, email = %(email)s, 
                        company_id = (SELECT id FROM IS601_MP3_Companies WHERE name=%(company_name)s LIMIT 1)
            """
            # Note: this reads the file as a stream instead of requiring us to save it
            stream = io.TextIOWrapper(file.stream._file, "UTF8", newline=None)
            # TODO importcsv-2 read the csv file stream as a dict
            # Gagan Indukala Krishna Murthy - gi36 - 6th April
            for row in csv.DictReader(stream, delimiter=','):
                # todo remove
                # print(row) #example
                # TODO importcsv-3 extract company data and append to company list 
                # as a dict only with company data if all is present
                # Gagan Indukala Krishna Murthy - gi36 - 6th April
                if row["company_name"] and row["address"] and row["city"] and row["state"] and row["zip"] and row["web"] and row["country"]:
                    companies.append({"name": row["company_name"], "address": row["address"], 
                                    "city": row["city"],"country": row["country"],"state": 
                                    row["state"],"zip": row["zip"],"website": row["web"]})
                # TODO importcsv-4 extract employee data and append to employee list 
                # as a dict only with employee data if all is present
                # Gagan Indukala Krishna Murthy - gi36 - 6th April
                if row["first_name"] and row["last_name"] and row["email"]:
                    employees.append({"first_name": row["first_name"],
                                    "last_name": row["last_name"], "email": row["email"],
                                    "company_name": row.get("company_name", None)})

            if len(companies) > 0:
                print(f"Inserting or updating {len(companies)} companies")
                try:
                    result = DB.insertMany(company_query, companies)
                    # TODO importcsv-5 display flash message about number of companies inserted
                    # Gagan Indukala Krishna Murthy - gi36 - 6th April
                    flash(f"Inserted {len(companies)} companies", "success")
                except Exception as e:
                    traceback.print_exc()
                    flash("There was an error loading in the csv data", "danger")
            else:
                # TODO importcsv-6 display flash message (info) that no companies were loaded
                # Gagan Indukala Krishna Murthy - gi36 - 6th April
                flash("No Companies were loaded", "success")
                pass
            if len(employees) > 0:
                print(f"Inserting or updating {len(employees)} employees")
                try:
                    result = DB.insertMany(employee_query, employees)
                    # TODO importcsv-7 display flash message about number of employees loaded
                    # Gagan Indukala Krishna Murthy - gi36 - 6th April
                    flash(f"Inserted {len(employees)} employees", "success")
                except Exception as e:
                    traceback.print_exc()
                    flash("There was an error loading in the csv data", "danger")
            else:
                # TODO importcsv-8 display flash message (info) that no companies were loaded
                # Gagan Indukala Krishna Murthy - gi36 - 6th April
                flash("No employees were loaded", "success")
                pass
            try:
                result = DB.selectOne("SHOW SESSION STATUS LIKE 'questions'")
                print(f"Result {result}")
            except Exception as e:
                    traceback.print_exc()
                    flash("There was an error counting session queries", "danger")
    return render_template("upload.html")
