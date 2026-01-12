import xlsxwriter
from io import BytesIO
from analytics import QuickCommerceAnalytics
from datetime import datetime

def create_excel_report():
    """Create comprehensive Excel report"""
    analytics = QuickCommerceAnalytics()
    
    try:
        # Create BytesIO object for in-memory Excel file
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'bg_color': '#E7E6E6'
        })
        
        cell_format = workbook.add_format({
            'border': 1,
            'align': 'left',
            'valign': 'vcenter'
        })
        
        number_format = workbook.add_format({
            'border': 1,
            'align': 'right',
            'valign': 'vcenter',
            'num_format': '0.00'
        })
        
        # Get all analytics data
        overview = analytics.get_overview_metrics()
        delays = analytics.get_order_delays_analysis()
        cancellations = analytics.get_cancellation_analysis()
        stockouts = analytics.get_stockout_analysis()
        riders = analytics.get_rider_performance()
        picking = analytics.get_picking_time_analysis()
        recommendations = analytics.get_recommendations()
        
        # SHEET 1: Overview
        overview_sheet = workbook.add_worksheet('Overview')
        overview_sheet.set_column('A:A', 30)
        overview_sheet.set_column('B:B', 20)
        
        overview_sheet.write('A1', 'Quick Commerce Analytics Report', title_format)
        overview_sheet.write('A2', f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}', cell_format)
        
        row = 4
        overview_sheet.write(row, 0, 'Metric', header_format)
        overview_sheet.write(row, 1, 'Value', header_format)
        row += 1
        
        for key, value in overview.items():
            overview_sheet.write(row, 0, key.replace('_', ' ').title(), cell_format)
            overview_sheet.write(row, 1, value, number_format)
            row += 1
        
        # SHEET 2: Order Delays
        delay_sheet = workbook.add_worksheet('Order Delays')
        delay_sheet.set_column('A:A', 30)
        delay_sheet.set_column('B:B', 15)
        
        delay_sheet.write('A1', 'Order Delays Analysis', title_format)
        
        row = 3
        delay_sheet.write(row, 0, 'Delay Category', header_format)
        delay_sheet.write(row, 1, 'Count', header_format)
        row += 1
        
        for category, count in delays.get('delay_distribution', {}).items():
            delay_sheet.write(row, 0, category.replace('_', ' ').title(), cell_format)
            delay_sheet.write(row, 1, count, number_format)
            row += 1
        
        row += 2
        delay_sheet.write(row, 0, 'Zone', header_format)
        delay_sheet.write(row, 1, 'Avg Delay (min)', header_format)
        delay_sheet.write(row, 2, 'Order Count', header_format)
        row += 1
        
        for zone, data in delays.get('delays_by_zone', {}).items():
            delay_sheet.write(row, 0, zone, cell_format)
            delay_sheet.write(row, 1, data['avg_delay'], number_format)
            delay_sheet.write(row, 2, data['count'], number_format)
            row += 1
        
        # SHEET 3: Cancellations
        cancel_sheet = workbook.add_worksheet('Cancellations')
        cancel_sheet.set_column('A:A', 30)
        cancel_sheet.set_column('B:B', 15)
        
        cancel_sheet.write('A1', 'Cancellation Analysis', title_format)
        
        row = 3
        cancel_sheet.write(row, 0, 'Reason', header_format)
        cancel_sheet.write(row, 1, 'Count', header_format)
        row += 1
        
        for reason, count in cancellations.get('cancellation_reasons', {}).items():
            cancel_sheet.write(row, 0, reason, cell_format)
            cancel_sheet.write(row, 1, count, number_format)
            row += 1
        
        # SHEET 4: Stockouts
        stockout_sheet = workbook.add_worksheet('Stockouts')
        stockout_sheet.set_column('A:A', 40)
        stockout_sheet.set_column('B:C', 20)
        
        stockout_sheet.write('A1', 'Stockout Analysis', title_format)
        
        row = 3
        stockout_sheet.write(row, 0, 'Product Name', header_format)
        stockout_sheet.write(row, 1, 'Department', header_format)
        stockout_sheet.write(row, 2, 'Stockout Count', header_format)
        row += 1
        
        for product in stockouts.get('top_stockout_products', []):
            stockout_sheet.write(row, 0, product['product_name'], cell_format)
            stockout_sheet.write(row, 1, product['department'], cell_format)
            stockout_sheet.write(row, 2, product['stockout_count'], number_format)
            row += 1
        
        # SHEET 5: Rider Performance
        rider_sheet = workbook.add_worksheet('Rider Performance')
        rider_sheet.set_column('A:A', 25)
        rider_sheet.set_column('B:D', 20)
        
        rider_sheet.write('A1', 'Rider Performance Analysis', title_format)
        
        row = 3
        rider_sheet.write(row, 0, 'Rider Name', header_format)
        rider_sheet.write(row, 1, 'Zone', header_format)
        rider_sheet.write(row, 2, 'Total Deliveries', header_format)
        rider_sheet.write(row, 3, 'Avg Delay (min)', header_format)
        row += 1
        
        for rider in riders.get('top_performers', []):
            rider_sheet.write(row, 0, rider['name'], cell_format)
            rider_sheet.write(row, 1, rider['zone'], cell_format)
            rider_sheet.write(row, 2, rider['total_deliveries'], number_format)
            rider_sheet.write(row, 3, rider['avg_delay'], number_format)
            row += 1
        
        # SHEET 6: Recommendations
        rec_sheet = workbook.add_worksheet('Recommendations')
        rec_sheet.set_column('A:A', 20)
        rec_sheet.set_column('B:B', 15)
        rec_sheet.set_column('C:D', 50)
        
        rec_sheet.write('A1', 'Data-Driven Recommendations', title_format)
        
        row = 3
        rec_sheet.write(row, 0, 'Category', header_format)
        rec_sheet.write(row, 1, 'Priority', header_format)
        rec_sheet.write(row, 2, 'Issue', header_format)
        rec_sheet.write(row, 3, 'Recommendation', header_format)
        row += 1
        
        for rec in recommendations:
            rec_sheet.write(row, 0, rec['category'], cell_format)
            rec_sheet.write(row, 1, rec['priority'], cell_format)
            rec_sheet.write(row, 2, rec['issue'], cell_format)
            rec_sheet.write(row, 3, rec['recommendation'], cell_format)
            row += 1
        
        workbook.close()
        output.seek(0)
        
        return output
        
    except Exception as e:
        print(f"Error creating Excel report: {e}")
        return None
    finally:
        analytics.close()
