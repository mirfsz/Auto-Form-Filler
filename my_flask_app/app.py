from flask import Flask, request, render_template
import re
import random
import statistics

app = Flask(__name__)


# Function to process the form data line by line, capturing user details
def process_form_data(data):
    lines = data.split("\n")
    users = []

    for line in lines:
        # Match the format: position, name, steps, and oxygen level
        match = re.match(r"(\d+)\s+([A-Za-z\s']+)\s*\|\s*(\d*)\s*steps?\s*\|\s*(\d*)%?", line.strip())

        if match:
            position = match.group(1)
            name = match.group(2).strip()
            steps = match.group(3)
            steps = int(steps) if steps else None
            oxygen = match.group(4)
            oxygen = int(oxygen) if oxygen else None
            users.append({"position": position, "name": name, "steps": steps, "oxygen": oxygen, "original_line": line})
        else:
            # Preserve non-matching lines as-is (e.g., headers, MC, etc.)
            users.append({"original_line": line})

    return users


# Function to calculate steps for "Irfan Mirzan" based on others' steps
def calculate_steps(steps):
    if len(steps) == 0:
        return 0  # If no data, return 0 as a fallback

    avg_steps = int(statistics.mean(steps))
    fluctuation = random.randint(-300, 300)
    return max(0, avg_steps + fluctuation)


# Function to randomly assign a blood oxygen level
def random_blood_oxygen():
    return random.choice([97, 98, 99])


# Function to reformat the data back to the original format with updated "Irfan Mirzan"
def format_report(users):
    formatted_data = []
    for user in users:
        if "original_line" in user and "name" in user and user['name'].lower() == "irfan mirzan":
            # Update Irfan Mirzan's line with the calculated steps and oxygen
            steps_text = f"{user['steps']} steps" if user['steps'] is not None else "steps"
            oxygen_text = f"{user['oxygen']}%" if user['oxygen'] is not None else ""
            formatted_data.append(f"{user['position']} {user['name']} | {steps_text} | {oxygen_text}")
        else:
            # Preserve other lines unchanged
            formatted_data.append(user['original_line'])

    return "\n".join(formatted_data)


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        form_data = request.form['data']

        # Process form data line by line
        users = process_form_data(form_data)

        # Get valid steps for calculating "Irfan Mirzan"'s steps
        all_steps = [user['steps'] for user in users if 'steps' in user and user['steps'] is not None]

        # Calculate "Irfan Mirzan"'s steps
        irfan_steps = calculate_steps(all_steps)
        irfan_oxygen = random_blood_oxygen()

        # Fill in "Irfan Mirzan" details in the users list
        for user in users:
            if 'name' in user and user['name'].lower() == "irfan mirzan":
                user['steps'] = irfan_steps
                user['oxygen'] = irfan_oxygen

        # Generate the full report
        full_report = format_report(users)

        return render_template("index.html", full_report=full_report)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)