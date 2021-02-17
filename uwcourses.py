"""Extracts UW course descriptions and exports them to CSV."""

import argparse
import collections
import csv
import io
import itertools
import logging
import re
import urllib.parse

import http.client
import lxml.html
import titlecase

COURSE_INDICES = {
    'Bothell': 'https://www.washington.edu/students/crscatb/',
    'Seattle': 'https://www.washington.edu/students/crscat/',
    'Tacoma': 'https://www.washington.edu/students/crscatt/'
}

Course = collections.namedtuple('Course', [
    'campus', 'department', 'code', 'name', 'credits', 'knowledge_areas',
    'prerequisites', 'offered'
])


def course_key(course):
  """Returns the course key.

  Args:
    course: The course object.

  Returns:
    A key that may be used to sort course objects.
  """
  return (course.campus, course.department, course.code)


def parse_credits(s):
  """Parses credit values from a string.

  Args:
    s: The string to parse.

  Returns:
    The credits as a number or None if the value could not be determined.
  """
  m = re.search(r'^(\d+)(?![-/])', s)
  return int(m.group(1)) if m else None


def parse_prerequisites(course_description):
  """Parses prerequisites from a course description.

  Args:
    course_description: The course description text.

  Returns:
    The course prerequisite codes.
  """
  if 'Prerequisite:' not in course_description:
    return []

  parts = course_description.split('Offered:')[0].split('Prerequisite:')
  return sorted(
      set([k.strip() for k in re.findall(r'([A-Z& ]+ \d+)', parts[1])]))


def parse_offered(course_description):
  """Parses which quarters a course is offered from a course description.

  Args:
    course_description: The course description text.

  Returns:
    The quarters the course is offered.
  """
  if 'Offered:' not in course_description:
    return []

  parts = course_description.split('Offered: ')
  if 'AWSpS.' in parts[1]:
    return ['A', 'W', 'Sp', 'S']
  elif 'AWSp.' in parts[1]:
    return ['A', 'W', 'Sp']
  elif 'AWS.' in parts[1]:
    return ['A', 'W', 'S']
  elif 'AW.' in parts[1]:
    return ['A', 'W']
  elif 'ASpS.' in parts[1]:
    return ['A', 'Sp', 'S']
  elif 'ASp.' in parts[1]:
    return ['A', 'Sp']
  elif 'AS.' in parts[1]:
    return ['A', 'S']
  elif 'A.' in parts[1]:
    return ['A']
  elif 'WSpS.' in parts[1]:
    return ['W', 'Sp', 'S']
  elif 'WSp.' in parts[1]:
    return ['W', 'Sp']
  elif 'WS.' in parts[1]:
    return ['W', 'S']
  elif 'W.' in parts[1]:
    return ['W']
  elif 'SpS.' in parts[1]:
    return ['Sp', 'S']
  elif 'Sp.' in parts[1]:
    return ['Sp']
  elif 'S.' in parts[1]:
    return ['S']

  return []


def parse_course(course_node, campus):
  """Parses course attributes from a DOM node.

  Args:
    course_node: The DOM node containing course information.
    campus: The name of the campus where the course is offered.

  Returns:
    A Course object.
  """
  (s, *remaining) = course_node.itertext()

  p = re.compile(r'^([A-Z& ]+) (\d+) (.+) \((.+).*\)(.*)$')
  m = p.match(s)
  if not m:
    logging.warning('Unable to parse title: %s', s)
    return

  department = m.group(1)
  code = m.group(2)
  title = titlecase.titlecase(m.group(3))
  crs = parse_credits(m.group(4))
  knowledge_areas = sorted([j.strip() for j in re.split(',|/', m.group(5))])
  prerequisites = parse_prerequisites(
      ''.join([j for j in remaining if 'Prerequisite:' in j]))
  offered = parse_offered(''.join([j for j in remaining if 'Offered:' in j]))
  return Course(campus, department, code, title, crs, knowledge_areas,
                prerequisites, offered)


def get_department_links(url):
  """Gets department links from the course index page.

  Args:
    url: The URL of the index page containing a list of departments.

  Returns:
    A set of department links found on the page.

  Raises:
    Exception: If an error occurred fetching the list of department links.
  """
  client = http.client.HTTPSConnection(url.netloc)
  client.request('GET', url.path)
  response = client.getresponse()
  if response.status != 200:
    raise Exception('Error reading index: %d %s' % (response.status,
                                                    response.read()))

  tree = lxml.html.fromstring(response.read())
  client.close()

  depts = tree.xpath(
      '/html/body/*/*/*/*/div[contains(@class, "uw-content")]//li/a')
  return set([i.get('href') for i in depts])


def get_courses(url, campus, dept_link):
  """Gets courses from a department's course description page.

  Args:
    url: The base URL for course descriptions.
    campus: The name of the department's campus.
    dept_link: A link to the department's course description page.

  Returns:
    A list of courses offered by the department.
  """
  client = http.client.HTTPSConnection(url.netloc)
  client.request('GET', '%s%s' % (url.path, dept_link))
  response = client.getresponse()
  if response.status != 200:
    logging.warning('Error reading category (%s): %d %s', dept_link,
                    response.status, response.read())
    return

  tree = lxml.html.fromstring(response.read())
  client.close()

  items = tree.xpath('/html/body/a/p')
  courses = []
  for i in items:
    course = parse_course(i, campus)
    if not course:
      logging.warning('Unable to parse course: %s', lxml.html.tostring(i))
      continue

    courses.append(course)

  return courses


def export_courses(courses, output):
  """Exports courses to CSV.

  Args:
    courses: A list of courses to be exported.
    output: The output buffer to which to write CSV data.
  """
  courses = sorted(courses, key=course_key)
  writer = csv.writer(output)
  writer.writerow([
      'Campus', 'Department', 'Code', 'Name', 'Credits', 'Areas of Knowledge',
      'Prerequisites', 'Offered'
  ])

  for course in courses:
    writer.writerow([
        course.campus, course.department, course.code, course.name,
        course.credits, ','.join(course.knowledge_areas),
        ','.join(course.prerequisites), ','.join(course.offered)
    ])


def validate_campus(value):
  """Ensures that a campus value is valid.

  Args:
    value: The campus value.

  Returns:
    The campus value.

  Raises:
    ArgumentTypeError: If an invalid campus value is found.
  """
  if value not in COURSE_INDICES:
    raise argparse.ArgumentTypeError(
        '%s is an invalid campus. Valid values include %s.' %
        (value, COURSE_INDICES.keys()))

  return value


def parse_arguments():
  """Parses and validates command line arguments.

  Returns:
    An object containing values for command line arguments.
  """
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--campus',
      type=validate_campus,
      dest='campuses',
      action='append',
      help='A list of campuses to scan for courses.')
  parser.add_argument(
      '--department_link',
      dest='department_links',
      action='append',
      help='A list of department links to scan for courses.')

  args = parser.parse_args()

  # args.campuses is not populated with a default because they are retained if
  # specific campuses are specified on the command line.
  if not args.campuses:
    args.campuses = COURSE_INDICES.keys()

  return args


def extract_courses(campuses, department_links):
  """Extracts course descriptions from the given campus and department links.

  Args:
    campuses: A list of campuses from which to extract course descriptions.
    department_links: A list of department links from which to extract course
        descriptions.

  Returns:
    A list of courses.
  """
  courses = []
  for campus in campuses:
    url = urllib.parse.urlparse(COURSE_INDICES[campus])
    depts = department_links if department_links else get_department_links(url)
    courses += list(
        itertools.chain.from_iterable(
            [get_courses(url, campus, i) for i in depts]))

  return courses


def main():
  """Extracts UW course descriptions and exports them to CSV."""
  args = parse_arguments()
  courses = extract_courses(args.campuses, args.department_links)
  output = io.StringIO()
  export_courses(courses, output)
  print(output.getvalue())
  output.close()


main()
