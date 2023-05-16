from flask import Flask, request, jsonify
from settings import handle_exceptions, logger, connection
from datetime import date

app = Flask(__name__)


# admit patient
@app.route("/admit_patient", methods=["POST"], endpoint="admit_patient")
@handle_exceptions
def admit_patient():
    cur, conn = connection()
    if  "name" and  "admit_date" and "discharge_date" not in request.json:
        raise Exception("data missing")
    logger(__name__).warning("starting the data base connection")
    data = request.get_json()
    name = data['name']
    admit_date = data['admit_date']
    discharge_date = data['discharge_date']
    cur.execute('INSERT INTO patient_data(name,admit_date,discharge_date)''VALUES (%s, %s, %s);',
                (name, admit_date, discharge_date))
    conn.commit()


# patient treatment
@app.route("/patient_treatment", methods=["POST"], endpoint="create_new_patient_treatment")
@handle_exceptions
def create_new_patient_treatment():
    cur, conn = connection()
    logger(__name__).warning("starting the data base connection")

    if "patient_id" and "treatment" and "treatment_date" not in request.json:
        raise Exception("data missing")

    data = request.get_json()
    patient_id = data.get('patient_id')
    treatment = data.get('treatment')
    treatment_date = data.get('treatment_date')

    query = "INSERT INTO treatment_data(patient_id, treatment, treatment_date) VALUES (%s, %s, %s);"
    values = (patient_id, treatment, treatment_date)

    cur.execute(query, values)

    conn.commit()
    logger(__name__).warning("close the database connection as treatment data is created")
    return jsonify("treatment data created   successfully")


@app.route("/all_patients", methods=["GET"], endpoint="all_patients")
@handle_exceptions
def all_patients():
    cur, conn = connection()
    cur.execute("SELECT * FROM patient_data ")
    patient_data = cur.fetchall()
    # Retrieve treatments for the patient from the treatment table
    cur.execute("SELECT * FROM treatment_data")
    treatments = cur.fetchall()
    data=[]
    patient_details = {
        "patient_data ": patient_data,
        "treatments": treatments,

    }
    data.append(patient_details)
    return jsonify(data),200


# get patient details
@app.route("/patient_details/<patient_id>", methods=["GET"], endpoint="get_patient_details")
def get_patient_details(patient_id):
    try:

        cur, conn = connection()

        # Retrieve patient details from the patient_data table
        cur.execute("SELECT * FROM patient_data WHERE patient_id = %s", (patient_id,))
        patient_data = cur.fetchone()
        # Retrieve treatments for the patient from the treatment table
        cur.execute("SELECT * FROM treatment_data WHERE patient_id = %s", (patient_id,))
        treatments = cur.fetchall()
        if not patient_data:
            return jsonify({"message": f"No rows found "})
        if not treatments:
            return jsonify({"message": f"No rows found "})
        data =[]
        # Create a dictionary to hold the patient details and treatments
        patient_details = {
            "patient_id": patient_id,
            "patient_data ": patient_data,
            "treatments": treatments,

        }
        data.append(patient_details)

        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Close the database connection
        cur.close()
        conn.close()


# update treatment
@app.route("/treatment/update/<int:treatment_id>", methods=["PUT"], endpoint="treatment_update")
def treatment_update(treatment_id):
    cur, conn = connection()
    logger(__name__).warning("starting the database connection")
    data = request.get_json()
    treatment = data['treatment']
    treatment_date = data['treatment_date']
    cur.execute('SELECT treatment,treatment_date FROM treatment_data WHERE treatment_id = %s', (treatment_id,))
    row = cur.fetchone()
    if not row:
        return jsonify({'message': 'treatment_id is not available'}), 400

    # Update the book's availability
    cur.execute('UPDATE treatment_data SET treatment=%s,treatment_date=%s WHERE treatment_id = %s', (treatment,treatment_date,treatment_id,))
    conn.commit()

    return jsonify({'message': 'updated successfully'}), 200


# update discharge_date
@app.route("/update/<int:patient_id>", methods=["PUT"], endpoint="discharge_update")
def treatment_update(patient_id):
    cur, conn = connection()
    logger(__name__).warning("starting the database connection")
    data = request.get_json()
    discharge_date = data['discharge_date']
    cur.execute('SELECT discharge_date FROM patient_data WHERE patient_id = %s', (patient_id ,))
    row = cur.fetchone()
    if not row:
        return jsonify({'message': 'patient_id is not available'}), 400
    # Update the book's availability
    cur.execute('UPDATE patient_data SET discharge_date=%s WHERE patient_id = %s', (discharge_date,patient_id,))
    conn.commit()

    return jsonify({'message': 'updated successfully'}), 200


# delete a patient
@app.route("/delete/<int:patient_id>", methods=["DELETE"], endpoint="delete_patient")
@handle_exceptions
def delete_patient(patient_id):
    cur, conn = connection()
    cur.execute("SELECT discharge_date FROM patient_data WHERE patient_id = %s", (patient_id,))
    discharge_date = cur.fetchone()[0]
    if discharge_date is not None and discharge_date < date.today():
        cur.execute("DELETE FROM patient_data WHERE patient_id = %s", (patient_id,))
        conn.commit()
        return "Patient record deleted successfully.", 200
    else:
        return "Patient cannot be deleted. Discharge date not crossed.", 400


@app.route("/treatments/delete/<int:treatment_id>",methods=["DELETE"],endpoint="delete_treatment_id")
def delete_treatment_id(treatment_id):
    cur, conn = connection()
    logger(__name__).warning("starting the database connection")
    cur.execute('DELETE FROM treatment_data WHERE treatment_id=%s', (treatment_id,))
    logger(__name__).warning("close the database connection")
    conn.commit()
    if cur.rowcount > 0:
        return jsonify({"message": "deleted successfully"})
    else:
        return jsonify({"message": "treatment_id  not found"})

