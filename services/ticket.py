from fpdf import FPDF
import os
from datetime import datetime

class TicketPDF(FPDF):
    def header(self):
        # Set background color for header area if needed
        self.set_fill_color(138, 43, 226)  # Purple theme
        self.rect(0, 0, 210, 40, 'F')
        
        self.set_font('Arial', 'B', 24)
        self.set_text_color(255, 255, 255)
        self.cell(0, 20, 'ShowGo Ticket', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()} | Generated on {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 0, 'C')

def generate_ticket_pdf(booking_id: int, movie_title: str, theatre_name: str, show_time: str, seats: str, total_amount: float) -> str:
    """
    Generates a PDF ticket and returns the absolute path to the file.
    """
    pdf = TicketPDF()
    pdf.add_page()
    
    # Body
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(0, 0, 0)
    
    pdf.ln(20)
    
    # Simple table-like structure
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(50, 10, 'Booking ID:', 0)
    pdf.set_font('Arial', '', 14)
    pdf.cell(0, 10, f'#BK-{booking_id}', 0, 1)
    
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(50, 10, 'Movie:', 0)
    pdf.set_font('Arial', '', 14)
    pdf.cell(0, 10, movie_title, 0, 1)
    
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(50, 10, 'Cinema:', 0)
    pdf.set_font('Arial', '', 14)
    pdf.cell(0, 10, theatre_name, 0, 1)
    
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(50, 10, 'Show Time:', 0)
    pdf.set_font('Arial', '', 14)
    pdf.cell(0, 10, show_time, 0, 1)
    
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(50, 10, 'Seats:', 0)
    pdf.set_font('Arial', '', 14)
    pdf.cell(0, 10, seats, 0, 1)
    
    pdf.ln(10)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)
    
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(50, 10, 'Total Paid:', 0)
    pdf.set_text_color(138, 43, 226)
    pdf.cell(0, 10, f'Rs. {total_amount:.2f}', 0, 1)
    
    # Instructions
    pdf.ln(20)
    pdf.set_font('Arial', 'I', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 5, 'Please present this PDF at the cinema counter to collect your physical ticket. Enjoy your movie!', 0, 'C')

    # Save to temp directory
    os.makedirs("/tmp/showgo_tickets", exist_ok=True)
    file_path = f"/tmp/showgo_tickets/ticket_{booking_id}.pdf"
    pdf.output(file_path)
    
    return file_path
