from dotenv import load_dotenv
import os
import requests
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

load_dotenv()

base_url = 'https://api.notion.com/v1'
database_id = '347f78d7da9e4869add0ae0834eba762'
api_key = os.getenv('NOTION_API_KEY')
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',
    'Notion-Version': '2022-06-28'
}

last_week = datetime.now() - timedelta(days=7)
last_week_iso = last_week.isoformat()

params = {
    'filter': {
        'property': 'Last edited time',
        'date': {
            'after': last_week_iso
        }
    }
}

response = requests.post(
    f'{base_url}/databases/{database_id}/query',
    headers=headers,
    json=params
)


tasks = response.json()['results']

project_times = {}
project_colors = {}

for task in tasks:   
  try:
    properties = task['properties']
    project = properties['Project']['select']['name']
    time_spent = properties['Time']['number']
    color = properties['Project']['select']['color']
  
    if time_spent == None:
      time_spent = 0
    
    if time_spent == 0:
      continue

    if project in project_times:
        project_times[project] += time_spent
    else:
        project_times[project] = time_spent
    
    project_colors[project] = color
  except TypeError: # may have missing props
    continue

# Generate the pie chart
labels = project_times.keys()
sizes = project_times.values()
colors = [project_colors[label] for label in labels]

# Define custom colors for the pie chart
color_palette = ['#FF7F0E', '#1F77B4', '#2CA02C', '#D62728', '#9467BD', '#8C564B', '#E377C2', '#7F7F7F', '#BCBD22', '#17BECF']
custom_colors = [color_palette[i % len(color_palette)] for i in range(len(labels))]

# Create a figure and axis with equal aspect ratio
fig, ax = plt.subplots(figsize=(8, 6), subplot_kw=dict(aspect='equal'))

# Generate the pie chart
wedges, text_labels, autotexts = ax.pie(sizes, labels=labels, colors=custom_colors, autopct='%1.1f%%', startangle=90)

# Set font properties for text labels and autotexts
font_props = {'size': 10, 'weight': 'bold'}
plt.setp(text_labels, fontproperties=font_props)
plt.setp(autotexts, fontproperties=font_props)

# Add a legend
ax.legend(wedges, labels, title='Projects', loc='center left', bbox_to_anchor=(1, 0, 0.5, 1))

# Add a title
ax.set_title('Time Spent on Projects')

# Save the plot as an image file
# Notion does not support uploading file via API
image_file = 'time_spent_pie.png'
plt.savefig(image_file, bbox_inches='tight')
