import tkinter as tk
from tkinter import ttk
from EjectionCalc import *


class Circle:
    def __init__(self, x, y, r, canvas, colour="black", label_text=""):
        self.x = x
        self.y = y
        self.r = r
        self.id = canvas.create_oval(x - r, y - r, x + r, y + r, fill=colour)
        self.label_id = canvas.create_text(x + r, y + r, text=label_text)

    def set_colour(self, colour, canvas):
        canvas.itemconfig(self.id, fill=colour)

    def set_label_text(self, label_text, canvas):
        canvas.itemconfig(self.label_id, text=label_text)

    def set_radius(self, radius, canvas):
        canvas.coords(self.id, self.x - radius, self.y - radius, self.x + radius, self.y + radius)

    def set_x(self, x, canvas):
        canvas.coords(self.id, x - self.r, self.y - self.r, x + self.r, self.y + self.r)
        self.x = x

    def set_y(self, y, canvas):
        canvas.coords(self.id, self.x - self.r, y - self.r, self.x + self.r, y + self.r)
        self.y = y


class Arrow:
    def __init__(self, x0, y0, x1, y1, canvas, colour="black", label_text=""):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.id = canvas.create_line(x0, y0, x1, y1, arrow=tk.LAST, fill=colour)
        self.label_id = canvas.create_text(x0 + 10, y1 - (y1 - y0) / 10, anchor="w", text=label_text)

    def set_label_text(self, label_text, canvas):
        canvas.itemconfig(self.label_id, text=label_text)


class Line:
    def __init__(self, x0, y0, x1, y1, canvas, colour="black"):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.id = canvas.create_line(x0, y0, x1, y1, fill=colour)

    def set_coords(self, x1, y1, x2, y2, canvas):
        canvas.coords(self.id, x1, y1, x2, y2)


class DropDown:
    def __init__(self, root, default, values, row=0, column=0, label_text="", label_right=True, command=None):
        self.default = default
        self.values = values

        if not default in values:
            self.values = [default] + self.values

        box = ttk.Combobox(root, values=self.values)
        box.bind("<<ComboboxSelected>>", command)
        box.set(value=default)
        box.grid(row=row, column=column)
        box.config(width=15)
        self.box = box

        offset = 2*label_right - 1
        label = tk.Label(root, text=label_text)
        label.grid(row=row, column=column+offset)
        self.label = label

    def get(self):
        return self.box.get()

    def set(self, index):
        self.box.current(index)


class Arc:
    def __init__(self, r, x, y, canvas, start=90, theta=0, label_text=""):
        self.x = x
        self.y = y
        self.r = r
        self.start = start
        self.theta = theta
        self.id = canvas.create_arc(x - r, y - r, x + r, y + r, start=start, extent=theta, width=1)

        try:
            self.label_id = canvas.create_text(x - 1.4 * self.r * abs(self.theta) / self.theta, y, text=label_text)

        except ZeroDivisionError:
            self.label_id = canvas.create_text(x + 1.4 * self.r, y, text=label_text)

    def set_start(self, start, canvas):
        canvas.itemconfig(self.id, start=math.degrees(start))

    def set_theta(self, theta, canvas):
        canvas.itemconfig(self.id, extent=math.degrees(theta))
        self.theta = math.degrees(theta)
        canvas.coords(self.label_id, self.x - 1.4 * self.r * abs(self.theta) / self.theta, self.y)

    def set_label_text(self, label_text, canvas):
        canvas.itemconfig(self.label_id, text=label_text)

    def set_radius(self, radius, canvas):
        self.r = radius
        canvas.coords(self.id, self.x - radius, self.y - radius, self.x + radius, self.y + radius)
        canvas.coords(self.label_id, self.x + 1.4 * self.r * abs(self.theta) / self.theta, self.y)


class IntInputBox:
    def __init__(self, row, column, root, min=-float("inf"), max=float("inf"), label_text="", label_right=True, required=False):
        self.__box = tk.Entry(root)
        self.__box.grid(row=row, column=column)

        self.__label = tk.Label(root, text=label_text)
        self.__label.grid(row=row, column=column + (2 * label_right - 1))
        self.__min = min
        self.__max = max
        self.__required = required

    def get(self):
        try:
            return int(self.__box.get()) / (self.__min <= int(self.__box.get()) <= self.__max)

        except ZeroDivisionError:
            print("Invalid value, assuming default values")

        except ValueError:
            if self.__box.get():
                print("Value must be an integer, assuming default values")

            elif self.__required:
                print("No value provided")

class TextBox:
    def __init__(self, row, column, root, default="", label_text="", label_right=True, width=15, height=1, rowspan=1, columnspan=1, bg="light grey"):
        self.__box = tk.Text(root, width=width, height=height, bg=bg)
        self.__box.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan)
        self.__box.insert(tk.END, default)
        self.__box.config(state=tk.DISABLED)

        self.__label = tk.Label(root, text=label_text)
        self.__label.grid(row=row, column=column + (2 * label_right - 1))

    def get(self):
        self.__box.get("1.0", tk.END)

    def set(self, text):
        self.__box.config(state=tk.NORMAL)
        self.clear()
        self.__box.insert(tk.END, text)
        self.__box.config(state=tk.DISABLED)

    def clear(self):
        self.__box.delete("1.0", tk.END)


class Table:
    def __init__(self, row, column, values, root, head=tuple(""), width=120, final_width=150):
        self.__head = head
        self.__values = values
        self.__table = ttk.Treeview(root, columns=head, height=35)
        self.__table.grid(row=row, column=column, rowspan=50)
        self.__table["show"] = "headings"
        self.__previous_clicked = None
        self.__descending = True
        self.__width = width
        self.__final_width = final_width
        self.__scrollbar_x = width * len(head) + abs((final_width - width) / 2)

        for name in self.__head:
            self.__table.column(name, width=self.__width, stretch=tk.NO)

        self.__table.column(self.__head[-1], width=self.__final_width, stretch=tk.NO)

        for name in self.__head:
            self.__table.heading(name, text=name)

        for counter, value in enumerate(values):
            self.__table.insert(parent="", index=counter, values=value)

        self.__table.bind("<Button-1>", self.__on_click)
        self.__table.bind("<Double-Button-1>", self.__on_double_click)

        self.__scrollbar = ttk.Scrollbar(root, orient="vertical",command=self.__table.yview)
        self.__scrollbar.place(x=self.__scrollbar_x, y=0, height=725)
        self.__table.config(yscrollcommand=self.__scrollbar.set)

    def __on_click(self, event):
        region = self.__table.identify("region", event.x, event.y)

        if region == "heading":
            column = self.__table.identify_column(event.x)
            column = int(column[1:]) - 1
            self.__sort(column)

            if self.__previous_clicked == column:
                self.__descending = not self.__descending

            else:
                self.__descending = True

            self.__table.delete(*self.__table.get_children())

            for name in self.__head:
                self.__table.column(name, width=120, stretch=tk.NO)

            self.__table.column(self.__head[-1], width=145, stretch=tk.NO)

            for counter, name in enumerate(self.__head):
                self.__table.heading(name, text=name)

            self.__table.heading(column, text=self.__head[column] + " ▼" * self.__descending + " ▲" * (not self.__descending))

            for counter, value in enumerate(self.__values):
                self.__table.insert(parent="", index=counter, values=value)

    def __sort(self, index):
        i = 1

        if self.__previous_clicked == index:
            self.__values = list(reversed(self.__values))

        else:
            while i < len(self.__values):
                j = i

                try:
                    while j > 0 and float(self.__values[j - 1][index]) > float(self.__values[j][index]):
                            self.__values[j], self.__values[j - 1] = self.__values[j - 1], self.__values[j]
                            j -= 1

                except ValueError:
                    while j > 0 and self.__values[j - 1][index] > self.__values[j][index]:
                            self.__values[j], self.__values[j - 1] = self.__values[j - 1], self.__values[j]
                            j -= 1

                i += 1

        self.__previous_clicked = index

    def __on_double_click(self, event):
        region = self.__table.identify("region", event.x, event.y)

        if region == "cell":
            current_item = self.__table.focus()
            item = list(self.__table.item(current_item).values())[2][:2]
            current_ui.mode_switch_box.box.current(0)
            current_ui.callback(None, default_origin=item[0], default_destination=item[1])

        elif region == "heading":
            self.__on_click(event)


class TransferCalcUI:
    def __init__(self, default_origin="", default_destination=""):
        self.__frame = tk.Frame(root)
        self.__frame.grid(row=0, column=0, rowspan=200, columnspan=30)
        self.name = "Calculate"
        self.__canvas = tk.Canvas(self.__frame, height=800, width=800)
        self.__canvas.grid(row=0, column=0, rowspan=200, columnspan=30)

        names = get_names()

        if default_origin:
            default_name1 = default_origin

        else:
            default_name1 = "Select a body"

        if default_destination:
            default_name2 = default_destination

        else:
            default_name2 = "Select a body"

        self.__name1 = DropDown(self.__frame, default_name1, names, label_text="Origin")
        self.__name2 = DropDown(self.__frame, default_name2, names, row=1, label_text="Destination")

        self.__x1, self.__y1, self.__x2, self.__y2 = 600, 150, 600, 550
        self.__ejection_arc = Arc(50, self.__x1, self.__y1, self.__canvas)
        self.__prograde_arrow = Arrow(self.__x1, self.__y2 - 300, self.__x1, self.__y2 - 500, self.__canvas)
        self.__body1_circle_1 = Circle(self.__x1, self.__y1, 10, self.__canvas, colour="")
        self.__init_orbit_circle = Circle(self.__x1, self.__y1, 25, self.__canvas, colour="")
        self.__spacecraft_circle = Circle(self.__x1, self.__y1 + self.__init_orbit_circle.r, 5, self.__canvas, colour="black")

        self.__orbit_circle_1 = Circle(self.__x2, self.__y2, self.__x1 * 0.1, self.__canvas, colour="")
        self.__orbit_circle_2 = Circle(self.__x2, self.__y2, self.__x1 * 0.2, self.__canvas, colour="")

        self.__phase_arc = Arc(self.__x2 * 0.1, self.__x2, self.__y2, self.__canvas, theta=0, start=0)
        self.__phase_line_1 = Line(self.__x2, self.__y2, self.__x2 * 1.1, self.__y2, self.__canvas)
        self.__phase_line_2 = Line(self.__x2, self.__y2, self.__x2 * 1.1, self.__y2, self.__canvas)

        self.__body1_circle_2 = Circle(self.__x2 * 1.1, self.__y2, 7, self.__canvas, colour="")
        self.__body2_circle = Circle(self.__x2 * 1.2, self.__y2, 7, self.__canvas, colour="")

        self.__host_circle = Circle(self.__x2, self.__y2, 5, self.__canvas, colour="orange")

        self.__init_alt_box = IntInputBox(2, 0, self.__frame, min=0, label_text="Parking orbit altitude")

        self.__final_alt_box = IntInputBox(3, 0, self.__frame, min=0, label_text="Final orbit altitude")

        self.__calculate = tk.Button(self.__frame, command=self.__update_bodies, text="Calculate", width=10)
        self.__calculate.grid(row=5, column=0)

        self.__swap = tk.Button(self.__frame, command=self.__swap_boxes, text="Swap", width=10)
        self.__swap.grid(row=6, column=0)

        self.__deltav_ejection_box = TextBox(7, 0, self.__frame, label_text="Ejection Δv", bg="white")
        self.__deltav_capture_box = TextBox(8, 0, self.__frame, label_text="Capture Δv", bg="white")
        self.__transfer_time_box = TextBox(9, 0, self.__frame, label_text="Travel Time", bg="white")

        ejection_explanation = "The ejection angle is the angle between the origin planet's prograde (direction of travel), and the point " \
                               "on your parking orbit you should burn."

        phase_explanation = "The phase angle is the angle, drawn from the origin planet to the Sun to the destination planet, " \
                            "that you should achieve before ejecting."

        self.__ejection_angle_explanation = TextBox(11, 10, self.__frame, default=ejection_explanation, width=40, height=5)
        self.__phase_angle_explanation = TextBox(190, 10, self.__frame, default=phase_explanation, width=40, height=5)

        if default_name1 and default_name2:
            self.__update_bodies()

    def __update_bodies(self):
        body1 = read_body(self.__name1.get())
        body2 = read_body(self.__name2.get())

        if body1:
            self.__body1_circle_1.set_colour(body1.get_colour(), self.__canvas)
            self.__body1_circle_2.set_colour(body1.get_colour(), self.__canvas)
            self.__prograde_arrow.set_label_text(body1.get_name() + " prograde", self.__canvas)

        if body2:
            self.__body2_circle.set_colour(body2.get_colour(), self.__canvas)

        if body1 and body2:
            if body2.get_SMA() > body1.get_SMA():
                self.__body1_circle_2.set_x(self.__x2 * 1.1, self.__canvas)
                self.__body2_circle.set_x(self.__x2 * 1.2, self.__canvas)

            else:
                self.__body1_circle_2.set_x(self.__x2 * 1.2, self.__canvas)
                self.__body2_circle.set_x(self.__x2 * 1.1, self.__canvas)

            self.__calculate_transfer()

    def __calculate_transfer(self):
        body1 = read_body(self.__name1.get())
        body2 = read_body(self.__name2.get())

        if body1 and body2:
            if self.__init_alt_box.get():
                body1.set_altitude(int(self.__init_alt_box.get()))

            if self.__final_alt_box.get():
                body2.set_altitude(int(self.__final_alt_box.get()))

            parking_orbit = Orbit(body1.get_radius() + body1.get_altitude(), body1.get_radius() + body1.get_altitude(), body1)
            target_orbit = Orbit(body2.get_radius() + body2.get_altitude(), body2.get_radius() + body2.get_altitude(), body2)

            transfer = Transfer(body1, body2, parking_orbit, target_orbit)

            ejection_angle = transfer.get_ejection_angle()
            phase_angle = transfer.get_phase_angle()

            if transfer.get_origin().get_SMA() < transfer.get_destination().get_SMA():
                self.__ejection_arc.set_theta(-ejection_angle, self.__canvas)
                self.__spacecraft_circle.set_x(self.__x1 + self.__init_orbit_circle.r * math.sin(ejection_angle), self.__canvas)
                self.__spacecraft_circle.set_y(self.__y1 - self.__init_orbit_circle.r * math.cos(ejection_angle), self.__canvas)
                self.__phase_line_2.set_coords(self.__phase_line_2.x0, self.__phase_line_2.y0, self.__x2 + self.__orbit_circle_2.r * math.cos(phase_angle),
                                               self.__y2 + self.__orbit_circle_2.r * math.sin(-phase_angle), self.__canvas)
                self.__phase_line_1.set_coords(self.__phase_line_1.x0, self.__phase_line_1.y0, self.__x2 + self.__orbit_circle_1.r, self.__y2, self.__canvas)

            else:
                ejection_angle = math.pi - ejection_angle
                self.__ejection_arc.set_theta(ejection_angle, self.__canvas)
                self.__spacecraft_circle.set_x(self.__x1 - self.__init_orbit_circle.r * math.sin(ejection_angle), self.__canvas)
                self.__spacecraft_circle.set_y(self.__y1 - self.__init_orbit_circle.r * math.cos(ejection_angle), self.__canvas)
                self.__phase_line_1.set_coords(self.__phase_line_1.x0, self.__phase_line_1.y0, self.__x2 + self.__orbit_circle_2.r, self.__y2, self.__canvas)
                self.__phase_line_2.set_coords(self.__phase_line_2.x0, self.__phase_line_2.y0, self.__x2 + self.__orbit_circle_1.r * math.cos(phase_angle),
                                               self.__y2 + self.__orbit_circle_1.r * math.sin(-phase_angle), self.__canvas)

            self.__ejection_arc.set_label_text(str(round(math.degrees(ejection_angle), 2)) + "°", self.__canvas)
            self.__phase_arc.set_label_text(str(round(math.degrees(phase_angle), 2)) + "°", self.__canvas)

            self.__phase_arc.set_theta(phase_angle, self.__canvas)
            self.__phase_arc.set_radius(self.__x2 * 0.1, self.__canvas)

            if body1.get_SMA() < body2.get_SMA():
                r2 = self.__x2 * 0.2

            else:
                r2 = self.__x2 * 0.1

            phase_angle = max(2*math.pi - phase_angle, phase_angle)

            self.__body2_circle.set_x(self.__x2 + r2 * math.cos(phase_angle), self.__canvas)
            self.__body2_circle.set_y(self.__y2 + r2 * math.sin(phase_angle), self.__canvas)

            self.__deltav_ejection_box.set(str(round(transfer.get_ejection_deltav(), 2)) + " m/s")
            self.__deltav_capture_box.set(str(round(transfer.get_capture_deltav(), 2)) + " m/s")
            self.__transfer_time_box.set(str(round(transfer.get_transfer_time() / 31536000, 3)) + " yr")

            # print(transfer)

    def __swap_boxes(self):
        indices = [self.__name2.box.current(), self.__name1.box.current()]
        self.__name1.box.current(indices[0])
        self.__name2.box.current(indices[1])
        self.__update_bodies()

    def end(self):
        self.__frame.destroy()


class SortingUI:
    def __init__(self):
        self.__frame = tk.Frame(root)
        self.__frame.grid(row=0, column=0, rowspan=200)
        self.name = "Sort"
        self.__bodies = get_names()


        # for i in self.__bodies[1:]:
        #     if i:
        #         print(read_body(i).get_name())

        self.__bodies = [read_body(c) for c in self.__bodies[1:] if c]
        self.__transfers = []

        for i in self.__bodies:
            for j in self.__bodies:
                if i.get_name() != j.get_name():
                    self.__transfers.append(Transfer(i, j, Orbit(i.get_altitude() + i.get_radius(), i.get_altitude() + i.get_radius(), i),
                                     Orbit(j.get_altitude() + j.get_radius(), j.get_altitude() + j.get_radius(), j)))

        columns = ("Origin", "Destination", "Ejection Δv (m/s)", "Capture Δv (m/s)", "Transfer Time (yr)")
        values = [(c.get_origin().get_name(), c.get_destination().get_name(), str(round(c.get_ejection_deltav(), 2)),
                   str(round(c.get_capture_deltav(), 2)), str(round(c.get_transfer_time() / 31536000, 3))) for c in self.__transfers]

        self.table = Table(0, 0, values, self.__frame, head=columns)

        # for i in self.__transfers:
        #     print(i.get_origin().get_name() + " -> " + i.get_destination().get_name())

    def end(self):
        self.__frame.destroy()


class UpdateUI:
    def __init__(self):
        self.__frame = tk.Frame(root)
        self.__frame.grid(row=0, column=0, rowspan=200, columnspan=30)
        self.name = "Update"

        self.__update_button = tk.Button(self.__frame, command=self.__update_bodies, text="Update", width=10)
        self.__update_button.grid(row=0, column=0)

    def end(self):
        self.__frame.destroy()
        
    def __add_body(self):
        return

    def __update_bodies(self):
        return


class UI:
    def __init__(self, ui):
        self.ui = ui
        self.mode_switch_box = DropDown(root, self.ui.name, mode_names, row=0, column=20, command=self.callback)

    def switch_ui(self, ui):
        self.ui.end()
        self.ui = ui

    def callback(self, value, default_origin="", default_destination=""):
        mode = self.mode_switch_box.get()

        if mode == "Calculate":
            self.switch_ui(TransferCalcUI(default_origin=default_origin, default_destination=default_destination))
            del self.mode_switch_box
            self.mode_switch_box = DropDown(root, "Calculate", mode_names, row=0, column=20, command=self.callback)

        elif mode == "Sort":
            self.switch_ui(SortingUI())

        else:
            self.switch_ui(UpdateUI())


if __name__ == "__main__":
    mode_names = ["Calculate", "Sort", "Update"]

    root = tk.Tk()
    root.geometry("800x800")

    current_ui = UI(TransferCalcUI())

    root.mainloop()

