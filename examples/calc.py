import csv
import statistics
from config import TESTING_PATH

def analyze_csv(filename):
    """Analyze testing.csv and calculate average end_ticks with certainty range."""
    end_ticks: list[float] = []
    
    try:
        with open(filename, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if 'end_ticks' in row:
                    try:
                        end_ticks.append(float(row['end_ticks']))
                    except ValueError:
                        continue
    except FileNotFoundError:
        print(f"Error: {filename} not found")
        return
    
    if not end_ticks:
        print("No valid end_ticks data found")
        return
    
    average = statistics.mean(end_ticks)
    stdev = statistics.stdev(end_ticks) if len(end_ticks) > 1 else 0
    
    # Calculate 95% confidence interval (approximately 2 * stdev)
    certainty_margin = 1.96 * stdev / (len(end_ticks) ** 0.5)
    
    print(f"Data Points: {len(end_ticks)}")
    print(f"Average end_ticks: {average:.4f}")
    print(f"Standard Deviation: {stdev:.4f}")
    print(f"Certainty Range (95%): {average - certainty_margin:.4f} to {average + certainty_margin:.4f}")

if __name__ == "__main__":
    analyze_csv(TESTING_PATH)
