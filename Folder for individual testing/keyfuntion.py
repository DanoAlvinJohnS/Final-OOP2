import pandas as pd

class LoadCourse:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_data(self):
        try:
            self.data = pd.read_excel(self.file_path)
            print("Data loaded successfully.")
        except Exception as e:
            print(f"Error loading data: {e}")

    def get_data(self):
        if self.data is not None:
            if 'Course Name' in self.data.columns:
                print("Course Names:                Course Number:")
                print(self.data['Course Name'] + "    " + self.data['Course Number'].astype(str))
            else:
                print("Column 'Course Name' not found.")
            return self.data
        else:
            print("No data loaded.")
            return None
        
class LoadJobs:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_data(self):
        try:
            self.data = pd.read_excel(self.file_path)
            print("Data loaded successfully.")
        except Exception as e:
            print(f"Error loading data: {e}")

    def get_data(self):
        if self.data is not None:
            if 'Job Title' in self.data.columns:
                print("Job Titles:                Company:")
                print(self.data['Job Title'] + "    " + self.data['Company'])
            else:
                print("Column 'Job Title' not found.")
            return self.data
        else:
            print("No data loaded.")
            return None
if __name__ == "__main__":
    reader = LoadCourse("sources/CPE_Courses.xlsx")
    reader.load_data()
    df = reader.get_data()
    print("\nFull DataFrame:")
    print(df)