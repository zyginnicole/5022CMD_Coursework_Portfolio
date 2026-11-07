"""
5022CMD Advanced Algorithms - Portfolio
Question 2: Graph (course prerequisite system)
"""

# Part 1: Graph data structure (generic graph structure that can be reused)
"""
Unweighted directed graph using a dictionary (adjacency list).
The vertices can be any data type (string, number, object, ...),
so this class can be reused in other programs.
"""
class Graph:
    def __init__(self):
        self.adjacency = {}

    def addVertex(self, vertex):
        # Add a new vertex, returns false if it already exists
        if vertex in self.adjacency:
            return False
        # new vertex starts with no edges
        self.adjacency[vertex] = []
        return True

    """
    Connect fromVertex -> toVertex.
    Returns True if the edge was added, 
    False if a vertex doesn't exist or the edge is already there
    """
    def addEdge(self, fromVertex, toVertex):
        if fromVertex not in self.adjacency or toVertex not in self.adjacency:
            return False

        if toVertex in self.adjacency[fromVertex]:
            return False

        self.adjacency[fromVertex].append(toVertex)
        return True

    """
    List all vertices that have an edge coming INTO the given vertex.
    The dictionary only stores outgoing edges, so we check every vertex's
    list to see if it contains the given vertex.
    """
    def listIncomingAdjVertex(self, vertex):
        incoming = []

        for other, neighbours in self.adjacency.items():
            if vertex in neighbours:
                incoming.append(other)
        return incoming

    """
    List all vertices that have an edge coming OUT the given vertex.
    In simple wrds, the values stored under the vertex's key.
    """
    def outgoingAdjVertex(self, vertex):
        return list(self.adjacency[vertex])

# Part 2: Course entity class
class Course:
    def __init__(self, courseCode, courseName, creditHours, level, description):
        self.courseCode = courseCode # str (e.g. CS101, unique)
        self.courseName = courseName # str (e.g. "Programming Fundamentals"
        self.creditHours = creditHours # int (e.g. 4, 6)
        self.level = level # str "Core" or "Elective"
        self.description = description #str, short summary of the course

    # called automatically by print (course)
    def __str__(self):
        return (f"Course Code  : {self.courseCode}\n"
                f"Course Name  : {self.courseName}\n"
                f"Credit Hours : {self.creditHours}\n"
                f"Level        : {self.level}\n"
                f"Description  : {self.description}")

# Part 3: Create the courses and the prerequisite graph
"""
Create 8 Course objects and store them in a dictionary.
The key is the course code, so a course can be found quickly
from the code the user types in.
"""
def createCourses():
    courseList = [
        Course("CS101", "Programming Fundamentals", 4, "Core",
               "Basic programming concepts using Python."),
        Course("CS102", "Discrete Mathematics", 3, "Core",
               "Logic, sets, relations and graphs."),
        Course("CS201", "Data Structures", 4, "Core",
               "Lists, stacks, queues, trees and hash tables."),
        Course("CS202", "Database Systems", 3, "Core",
               "Relational databases and SQL."),
        Course("CS301", "Advanced Algorithms", 4, "Core",
               "Algorithm design and complexity analysis."),
        Course("CS302", "Operating Systems", 3, "Core",
               "Processes, threads and memory management."),
        Course("CS303", "Artificial Intelligence", 3, "Elective",
               "Search, reasoning and machine learning basics."),
        Course("CS304", "Cloud Computing", 3, "Elective",
               "Cloud services and distributed systems."),
    ]
    courses = {}
    for c in courseList:
        courses[c.courseCode] = c
    return courses


"""
Build the prerequisite graph.
Each vertex is a course code. An edge  X -> Y  means
"X must be completed before Y".
"""
def createGraph (courses):
    graph = Graph()

    # Add one vertex for every course
    for code in courses:
        graph.addVertex(code)

    # Add the prerequisite edges
    prerequisites = [
        ("CS101", "CS201"),  # Programming Fundamentals -> Data Structures
        ("CS101", "CS202"),  # Programming Fundamentals -> Database Systems
        ("CS201", "CS301"),  # Data Structures          -> Advanced Algorithms
        ("CS102", "CS301"),  # Discrete Mathematics     -> Advanced Algorithms
        ("CS201", "CS302"),  # Data Structures          -> Operating Systems
        ("CS301", "CS303"),  # Advanced Algorithms      -> Artificial Intelligence
        ("CS202", "CS304"),  # Database Systems         -> Cloud Computing
        ("CS302", "CS304"),  # Operating Systems        -> Cloud Computing
    ]

    for prereq, unlocked in prerequisites:
        graph.addEdge(prereq, unlocked)

    return graph

# Part 4: Menu features
"""Ask the user for a course code. Returns the code, or None if invalid."""
def enterCourseCode(courses, prompt):
    code = input(prompt).strip().upper()          # strip spaces, make uppercase
    if code not in courses:                       # check the dictionary
        print(f"Course '{code}' does not exist.")
        return None

    return code

"""Print a list of course codes with their names."""
def printCourseList(codes, courses, msg):
    if len(codes) == 0:
        print(msg)
        return
    for c in codes:
        print(f"{c}: {courses[c].courseName}")

"""Display all course names"""
def displayAllCourses(courses):
    print("\n--- All Courses ---")
    for code in courses:
        print(f"{code} - {courses[code].courseName}")

"""View details of one course"""
def viewCourseDetails(courses):
    print("\n--- View Course Details ---")
    code = enterCourseCode(courses, "Enter course code: ")
    if code is None:
        return
    print()
    print(courses[code]) # will call the __str__

"""View Prerequisites (incoming edges)"""
def viewPrerequisites(graph, courses):
    print("\n--- View Prerequisites ---")
    code = enterCourseCode(courses, "Enter course code: ")
    if code is None:
        return
    # store incoming edges
    prerequisites = graph.listIncomingAdjVertex(code)
    print(f"\nPrerequisites of {code} ({courses[code].courseName}): ")
    printCourseList(prerequisites, courses, "None (no prerequisite needed)")

"""View Unlocked Courses (outgoing edges)"""
def viewUnlockedCourses(graph, courses):
    print("\n--- View Unlocked Courses ---")

    code = enterCourseCode(courses, "Enter course code: ")
    if code is None:
        return

    unlocked = graph.outgoingAdjVertex(code)
    print(f"\nCourses unlocked by {code} ({courses[code].courseName}): ")
    printCourseList(unlocked, courses, "None (this course is not a prerequisite for other courses)")

"""Add prerequisite on demand"""
def addPrerequisite(graph, courses):
    print("\n--- Add a Prerequisite ---")
    course = enterCourseCode(courses, "Enter a course that needs a new prerequisite: ")
    if course is None:
        return

    prerequisite = enterCourseCode(courses, "Course to add as the prerequisite: ")
    if prerequisite is None:
        return

    # First check: a course cannot be its own prerequisite
    if course == prerequisite:
        print("A course cannot be a prerequisite of itself.")
        return

    # Second check: edges cannot exist
    if prerequisite in graph.listIncomingAdjVertex(course):
        print(f"{prerequisite} is already a prerequisite of {course}")
        return

    # Third check, avoid circular structure
    if course in graph.listIncomingAdjVertex(prerequisite):
        print(f"Not allowed: {prerequisite} already requires {course}, "
              f"so this would be circular.")
        return

    graph.addEdge(prerequisite, course)
    print(f"{prerequisite} is now a prerequisite of {course}.")

# Part 5: Menu-driven program
def main():
    courses = createCourses()
    graph = createGraph(courses)

    while True:
        print("\n===== COURSE PREREQUISITE SYSTEM =====")
        print("1. Display all courses")
        print("2. View course details")
        print("3. View prerequisites of a course")
        print("4. View courses unlocked by a course")
        print("5. Add a prerequisite to a course")
        print("0. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            displayAllCourses(courses)
        elif choice == "2":
            viewCourseDetails(courses)
        elif choice == "3":
            viewPrerequisites(graph, courses)
        elif choice == "4":
            viewUnlockedCourses(graph, courses)
        elif choice == "5":
            addPrerequisite(graph, courses)
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid option, please try again (0 - 5).")

if __name__ == "__main__":
    main()