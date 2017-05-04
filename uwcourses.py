"""Extracts UW course descriptions and exports them to CSV."""

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
    'Bothell': 'http://www.washington.edu/students/crscatb/',
    'Seattle': 'http://www.washington.edu/students/crscat/',
    'Tacoma': 'http://www.washington.edu/students/crscatt/'
}

Course = collections.namedtuple('Course',
                                ['campus', 'code', 'name', 'credits', 'areas'])


def course_key(course):
  """Returns the course key.

  Args:
    course: The course object.

  Returns: A key that may be used to sort course objects.
  """
  return (course.campus, course.code)


def parse_credits(s):
  """Parses credit values from a string.

  Args:
    s: The string to parse.

  Returns: The credits as a number or None if the value could not be determined.
  """
  m = re.search(r'^(\d+)(?![-/])', s)
  return int(m.group(1)) if m else None


def get_department_links(url):
  """Gets department links from the course index page.

  Args:
    url: The URL of the index page containing a list of departments.

  Returns: A set of department links found on the page.
  """
  client = http.client.HTTPConnection(url.netloc)
  client.request('GET', url.path)
  response = client.getresponse()
  if response.status != 200:
    raise Exception('Error reading index: %d %s' % (response.status,
                                                    response.read()))

  tree = lxml.html.fromstring(response.read())
  client.close()

  depts = tree.xpath('//*[contains(@class, "uw-content")]/ul/li//a')
  return set([i.get('href') for i in depts])


def get_courses(url, campus, dept_link):
  """Gets courses from a department's course description page.

  Args:
    url: The base URL for course descriptions.
    campus: The name of the department's campus.
    dept_link: A link to the department's course description page.

  Returns: A list of courses offered by the department.
  """
  client = http.client.HTTPConnection(url.netloc)
  client.request('GET', '%s%s' % (url.path, dept_link))
  response = client.getresponse()
  if response.status != 200:
    raise Exception('Error reading category: %d %s' % (response.status,
                                                       response.read()))

  tree = lxml.html.fromstring(response.read())
  client.close()

  titles = [i.text for i in tree.xpath('//p//b')]

  courses = []
  p = re.compile(r'^([A-Z& ]+ \d+) (.+) \((.+).*\)(.*)$')
  for i in titles:
    m = p.match(i)
    if not m:
      logging.warning('Unable to parse title: %s', i)
      continue

    areas = sorted([j.strip() for j in re.split(',|/', m.group(4))])
    courses.append(
        Course(campus,
               m.group(1),
               titlecase.titlecase(m.group(2)),
               parse_credits(m.group(3)), areas))

  return courses


def export_courses(courses, output):
  """Exports courses to CSV.

  Args:
    courses: A list of courses to be exported.
    output: The output buffer to which to write CSV data.
  """
  courses = sorted(courses, key=course_key)
  writer = csv.writer(output)
  writer.writerow(['Campus', 'Code', 'Name', 'Credits', 'Areas of Knowledge'])

  for course in courses:
    writer.writerow([
        course.campus, course.code, course.name, course.credits,
        ','.join(course.areas)
    ])


def main():
  """Extracts UW course descriptions and exports them to CSV."""

  # Extract UW courses.
  courses = []
  for key in COURSE_INDICES:
    url = urllib.parse.urlparse(COURSE_INDICES[key])
    courses += list(
        itertools.chain.from_iterable(
            [get_courses(url, key, i) for i in get_department_links(url)]))

  # Export courses to CSV.
  output = io.StringIO()
  export_courses(courses, output)
  print(output.getvalue())
  output.close()


main()
