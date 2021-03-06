#!/usr/bin/env python3
import json
import locale
import os, sys
import reports
import emails

def load_data(filename):
    """Loads the contents of filename as a JSON file."""
    with open(filename, encoding='utf-8') as json_file:
        data = json.load(json_file)
        sort_data = sorted(data, key = lambda i: i['total_sales'], reverse=True)

    return sort_data

def format_car(car):
    """Given a car dictionary, returns a nicely formatted name."""
    return "{} {} ({})".format(car["car_make"], car["car_model"], car["car_year"])

def process_data(data):
    """
    Analyzes the data, looking for maximums.
    Returns a list of lines that summarize the information.
    """
    locale.setlocale(locale.LC_ALL, "C.UTF-8")
    max_revenue = {"revenue": 0} 
    max_sale = {"total_sales": 0}
    best_car = {}

    for item in data:
        # Calculate the revenue generated by this model (price * total_sales)
        # We need to convert the price from "$1234.56" to 1234.56
        item_price = locale.atof(item["price"].strip("$")) # extract price
        item_revenue = item["total_sales"] * item_price # get revenue per item

        # compare if current item_revnue is greater than max revenue
        if item_revenue > max_revenue["revenue"]:  
            item["revenue"] = item_revenue
            max_revenue = item
        # comapre total_sale of current item and max_sale's total_sale
        if item["total_sales"] > max_sale["total_sales"]:
            max_sale = item
        # get the most popular car_year
        if not item["car"]["car_year"] in best_car.keys():
            best_car[item["car"]["car_year"]] = item["total_sales"]
        else:
            best_car[item["car"]["car_year"]] += item["total_sales"]
        
        all_values = best_car.values()
        max_value = max(all_values)
        max_key = max(best_car, key=best_car.get)

    summary = [
        "The {} generated the most revenue: ${}".format(format_car(max_revenue["car"]), max_revenue["revenue"]),
        "The {} {} ({}) had the most sales: {}".format((max_sale["car"]["car_make"]), (max_sale['car']['car_model']),
                                                       (max_sale['car']['car_year']), (max_sale["total_sales"]) ),
        "The most popular year was {} with {} sales.".format(max_key, max_value),
        ]

    return summary

def cars_dict_to_table(car_data):
    """Turns the data in car_data into a list of lists or two-dimensional array."""
    table_data = [["ID", "Car", "Price", "Total Sales"]]
    for item in car_data:
        table_data.append([item["id"], format_car(item["car"]), item["price"], item["total_sales"]])

    return table_data

def main(argv):
    """Process the JSON data and generate a full report out of it."""
    # load json data
    data = load_data("car_sales.json")
    # process data and generate summary report
    summary = process_data(data)
    # formatting the content of summary report
    all_summary = '<br/> \n'.join(summary) 
    print(summary)
    # convert turn this into a PDF report
    reports.generate("/tmp/cars.pdf", "Cars report", all_summary, cars_dict_to_table(data))
    # send the PDF report as an email attachment
    sender = "automation@example.com"
    receiver = "{}@example.com".format(os.environ.get('USER'))
    subject = "Sales summary for last month"
    # generate email content and attach cars.pdf
    message = emails.generate(sender, receiver, subject, all_summary, "/tmp/cars.pdf")
    emails.send(message) # send an email to a concerned email address


if __name__ == "__main__":
    main(sys.argv)
