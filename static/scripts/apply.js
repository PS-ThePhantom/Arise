//+-----------------------------------------------------------------------------+
//| HTML ELEMENTS DECLARATIONS                                                  |
//+-----------------------------------------------------------------------------+
const calMonthDisplay = document.getElementById('month-year-display');
const calPrevMonthButton = document.getElementById('prev-month-btn');
const calNextMonthButton = document.getElementById('next-month-btn');
const calRefreshButton = document.getElementById('dt-retry-btn');
const calLoader = document.getElementById('dt-loader');
const calError = document.getElementById('dt-error');
const datePicker = document.getElementById('calendar-days-container');
const timePicker = document.getElementById('time-picker');
const formCarousel = document.querySelector('#form-carousel');
const formNextButton = document.getElementById('form-next-btn');
const formBackButton = document.getElementById('form-back-btn');
const personalInfoForm = document.getElementById('personal-info');
const businessInfoForm = document.getElementById('business-info');
const bookingDateForm = document.getElementById('date-time-info');
const firstName = document.getElementById('first-name');
const lastName = document.getElementById('last-name');
const email = document.getElementById('email');
const phone = document.getElementById('phone');
const service = document.getElementById('service');
const type = document.getElementById('type');
const companyName = document.getElementById('company');
const companyAge = document.getElementById('company-age');
const companyRevenue = document.getElementById('business-revenue');
const formErrorMessage = document.getElementById('form-error');

//+-----------------------------------------------------------------------------+
//| VARIABLES & INITIAL VALUES                                                  |
//+-----------------------------------------------------------------------------+

//months Names in order
const months = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
];

//enum for calendar direction
//either going forward to next month
//or going backward to previous month
const calDirection = Object.freeze({
    FORWARD: "FORWARD",
    BACKWARD: "BACKWARD"
});

//calendar state
const selectedBookingMonth = {
    "month": new Date().getMonth() + 1,
    "year": new Date().getFullYear()
};

const minBookingMonth = {
    "month": selectedBookingMonth.month,
    "year": selectedBookingMonth.year
};

const maxBookingMonth = {
    "month": null,
    "year": null
};

const selectedDate = {
    "year": null,
    "month": null,
    "day": null
};

const selectedTimeSlot = {
    "year": null,
    "month": null,
    "day": null,
    "time": null
};

let availableSlots = null;
let currentFormStep = 0;

//+-----------------------------------------------------------------------------+
//| FUNCTIONS                                                                   |
//+-----------------------------------------------------------------------------+

//function to fetch max booking date from server
const fetchMaxBookingMonth = async () => {
    try {
        const response = await fetch('/api/last-possible-booking-date');

        if (!response.ok) {
            toggleCalError()
            return;
        }

        const data = await response.json();

        //check if theres a limit on booking dates
        if (data.limit) {
            maxBookingMonth.month = data.month;
            maxBookingMonth.year = data.year;
        } else {
            maxBookingMonth.month = null;
            maxBookingMonth.year = null;
        }

    } catch (error) {
        toggleCalError();
    }
};

//refresh calendar in case of error, or first load
const calRefresh = async () => {
    await fetchMaxBookingMonth();

    //check if we are fully booked, if so reset dates
    //ensures that refreshes only refreshes current month if an error occurs
    //but when fully booked we should check all months for an available space
    if (minBookingMonth.month === maxBookingMonth.month && minBookingMonth.year === maxBookingMonth.year) {
        selectedBookingMonth.month = new Date().getMonth() + 1;
        selectedBookingMonth.year = new Date().getFullYear();

        minBookingMonth.month = selectedBookingMonth.month;
        minBookingMonth.year = selectedBookingMonth.year;
    }

    //load calendar
    setCalMonth(selectedBookingMonth.month, selectedBookingMonth.year);
}

//next and previous month function
const goToNextBookingMonth = (currentMonth = null) => {
    //next month date
    const nextMonth = { "month": selectedBookingMonth.month + 1, "year": selectedBookingMonth.year };
    if (currentMonth) {
        nextMonth.month = currentMonth.month + 1;
        nextMonth.year = currentMonth.year;
    }

    if (nextMonth.month > 12) {
        nextMonth.month = 1;
        nextMonth.year += 1;
    }

    //check if next month is within booking range
    if (maxBookingMonth.year && maxBookingMonth.month) {
        if (nextMonth.year > maxBookingMonth.year || (nextMonth.year === maxBookingMonth.year && nextMonth.month > maxBookingMonth.month)) {
            calNextMonthButton.disabled = true;
            return;
        }
    } else {
        displayError('Unable to load calendar. Please try again later or refresh the calendar.');
        return;
    }

    //update calendar display
    calMonthDisplay.textContent = `${months[nextMonth.month - 1]} ${nextMonth.year}`;
    selectedBookingMonth.month = nextMonth.month;
    selectedBookingMonth.year = nextMonth.year;

    //load calendar
    setCalMonth(selectedBookingMonth.month, selectedBookingMonth.year);
};



const goToPrevBookingMonth = (currentMonth = null) => {
    //previous month date
    const prevMonth = { "month": selectedBookingMonth.month - 1, "year": selectedBookingMonth.year };
    if (currentMonth) {
        prevMonth.month = currentMonth.month - 1;
        prevMonth.year = currentMonth.year;
    }

    if (prevMonth.month < 1) {
        prevMonth.month = 12;
        prevMonth.year -= 1;
    }

    //check if previous month is within booking range
    if (prevMonth.year < minBookingMonth.year || (prevMonth.year === minBookingMonth.year && prevMonth.month < minBookingMonth.month)) {
        calPrevMonthButton.disabled = true;
        return;
    }

    //update calendar display
    calMonthDisplay.textContent = `${months[prevMonth.month - 1]} ${prevMonth.year}`;
    selectedBookingMonth.month = prevMonth.month;
    selectedBookingMonth.year = prevMonth.year;

    //load calendar
    setCalMonth(selectedBookingMonth.month, selectedBookingMonth.year);
};

//functions to toggle calendar loader visibility
//hides error, date and time picker when showing loader
const toggleCalLoader = (show = true) => {
    if (show) {
        if (calLoader.classList.contains('hidden')) {
            calLoader.classList.remove('hidden');
        }

        //hide error, date and time picker if visible
        toggleCalError(false);
        toggleDateTimePicker(false);
    } else if (!show && !calLoader.classList.contains('hidden')) {
        calLoader.classList.add('hidden');
    }
};

//functions to toggle date and time picker visibility
//hides loader and error when showing pickers
const toggleDateTimePicker = (show = true) => {
    if (show) {
        //show date picker
        if (datePicker.classList.contains('hidden')) {
            datePicker.classList.remove('hidden');
        }

        //show time picker
        if (timePicker.classList.contains('hidden')) {
            timePicker.classList.remove('hidden');
        }

        //hide loader and error if visible
        toggleCalLoader(false);
        toggleCalError(false);
    } else {
        //hide date picker
        if (!datePicker.classList.contains('hidden')) {
            datePicker.classList.add('hidden');
        }

        //hide time picker
        if (!timePicker.classList.contains('hidden')) {
            timePicker.classList.add('hidden');
        }
    }
};

//functions to toggle calendar error visibility
//hides loader and date/time picker when showing error
const toggleCalError = (show = true, error = null) => {
    //set error message if provided
    if (error) {
        calError.querySelector('.error-text').textContent = error;
    } else {
        calError.querySelector('.error-text').textContent = 'Failed to load calendar. Please try again later.';
    }

    if (show) {
        if (calError.classList.contains('hidden')) {
            calError.classList.remove('hidden');
        }

        //hide loader, date and time picker if visible
        toggleCalLoader(false);
        toggleDateTimePicker(false);
    } else if (!show && !calError.classList.contains('hidden')) {
        calError.classList.add('hidden');
    }
};

//get next month
const getNextMonth = (month, year) => {
    const nextMonth = { "month": month + 1, "year": year };

    if (nextMonth.month > 12) {
        nextMonth.month = 1;
        nextMonth.year += 1;
    }

    return nextMonth;
}

//get prev month
const getPrevMonth = (month, year) => {
    const prevMonth = { "month": month + 1, "year": year };

    if (prevMonth.month < 1) {
        prevMonth.month = 12;
        prevMonth.year -= 1;
    }

    return prevMonth;
}

const selectDate = (month, year, day) => {
    selectedDate.day = day;
    selectedDate.month = month;
    selectedDate.year = year;

    const activeDay = datePicker.querySelector(".active-day");
    if (activeDay) {
        activeDay.classList.remove('active-day');
        activeDay.disabled = false;
    }

    const currentDay = Array.from(datePicker.querySelectorAll(".cal-days")).filter(e => {
        return Number(e.textContent, 10) === day && Number(e.dataset.date.split('-')[1], 10) === month;
    })[0];
    currentDay.classList.add('active-day');
    currentDay.disabled = true;

    populateCalTimes(month, year);
}

//populate calendar
const populateCalDays = (month, year) => {
    //clear calendar
    datePicker.innerHTML = '';
    timePicker.innerHTML = '';

    const startDay = new Date(year, month - 1, 1).getDay();
    const endDate = new Date(year, month, 0).getDate();
    const endDay = new Date(year, month - 1, endDate).getDay();
    const endDatePrevMonth = new Date(year, month - 1, 0).getDate();

    //create a calendar day button
    const addDayBtn = (year, month, day, disable = false, btnClass = null) => {
        const dayBtn = document.createElement('button');
        dayBtn.textContent = day;
        dayBtn.disabled = disable;
        btnClass ? dayBtn.classList.add('cal-days', btnClass) : dayBtn.classList.add('cal-days');
        dayBtn.dataset.date = `${year}-${month}-${day}`;

        if (year === selectedTimeSlot.year && month === selectedTimeSlot.month && day === selectedTimeSlot.day) {
            dayBtn.classList.add('selected-DT');
        }

        datePicker.appendChild(dayBtn);
    };

    //populate Previous month's last days for current months first week
    for (let i = endDatePrevMonth - startDay + 1; i <= endDatePrevMonth; i++) {
        addDayBtn(year, month - 1, i, true, 'filler-day');
    }

    //populate Current month's days
    const todaysDate = new Date();

    for (const index of availableSlots) {
        const today = year === todaysDate.getFullYear() && month === todaysDate.getMonth() + 1 && index.day === todaysDate.getDate();

        if (!index.slots.length > 0) {
            addDayBtn(year, month, index.day, true, today ? 'current-day' : 'inactive-day');
            continue;
        }

        if (selectedDate.day === null || (selectedDate.day === index.day && selectedDate.month === month && selectedDate.year === year)) {
            addDayBtn(year, month, index.day);
            selectDate(month, year, index.day);
            continue;
        }

        addDayBtn(year, month, index.day, false, today ? 'current-day' : null);
    }

    //populate next month's first days for current months last week
    for (let i = 0; i < 6 - endDay; i++) {
        addDayBtn(year, month + 1, i + 1, true, 'filler-day');
    }
};

const populateCalTimes = (month, year) => {
    //clear time
    timePicker.innerHTML = '';

    if (year != selectedDate.year || month != selectedDate.month || !availableSlots) {
        return;
    }

    for (const timeSlot of availableSlots[selectedDate.day - 1].slots) {
        const timeBtn = document.createElement('button');
        timeBtn.classList.add('cal-time');
        timeBtn.textContent = timeSlot;
        timeBtn.dataset.dateTime = `${year}-${month}-${selectedDate.day} ${timeSlot}`;

        if (selectedTimeSlot.year === selectedDate.year && selectedTimeSlot.month === selectedDate.month
            && selectedTimeSlot.day === selectedDate.day && selectedTimeSlot.time === timeSlot) {
            timeBtn.classList.add('cal-time-active');
            timeBtn.disabled = true;
        }

        timePicker.appendChild(timeBtn)
    }
}

//change calendar month selection
const setCalMonth = async (month, year, direction = calDirection.FORWARD) => {
    //update calendar display
    calMonthDisplay.textContent = `${months[month - 1]} ${year}`;
    selectedBookingMonth.month = month;
    selectedBookingMonth.year = year;

    toggleCalLoader(); //show loader

    //check if we are at the booking min limits and enable or disable prev month button
    if (!calPrevMonthButton.disabled && minBookingMonth.year === year && minBookingMonth.month === month) {
        calPrevMonthButton.disabled = true;
    } else if (calPrevMonthButton.disabled && (minBookingMonth.year != year || minBookingMonth.month != month)) {
        calPrevMonthButton.disabled = false;
    }

    if (!calNextMonthButton.disabled && maxBookingMonth.year === year && maxBookingMonth.month === month) {
        calNextMonthButton.disabled = true;
    } else if (calNextMonthButton.disabled && (maxBookingMonth.year != year || maxBookingMonth.month != month)) {
        calNextMonthButton.disabled = false;
    }

    //get all the slots available for current month
    let slotAvailable = false;
    try {
        const response = await fetch(`/api/free-slots?month=${month}&year=${year}`);

        if (!response.ok) {
            //display error message returned from server
            if (response.status === 400) {
                const errorData = await response.json();
                toggleCalError(true, errorData.error);
            } else {
                toggleCalError();
            }

            return;
        }

        //get calendar info
        const data = await response.json();

        availableSlots = data.slots;

        //check if there are available slots
        for (const day in availableSlots) {
            if (availableSlots[day].slots.length > 0) {
                slotAvailable = true;
                break;
            }
        }

    } catch (error) {
        toggleCalError();
        return;
    }

    //if no slot is available
    if (!slotAvailable) {
        //check if we are fully booked for the for the allowed months
        if (maxBookingMonth.year === minBookingMonth.year && maxBookingMonth.month === minBookingMonth.month) {
            toggleCalError(true, `Sorry, We are fully booked from now untill ${months[month - 1]} ${year}. Please try again later or contact us to book an appointment by emailing: info@ariseconsulting.co.za`);
            return;
        }

        //check if current month is the lower limit, if it is then update lower limits and go to the next month
        const nextMonth = getNextMonth(month, year);

        if (minBookingMonth.year === year && minBookingMonth.month === month) {
            minBookingMonth.month = nextMonth.month;
            minBookingMonth.year = nextMonth.year;

            setCalMonth(nextMonth.month, nextMonth.year);
            return;
        }

        //check if current month is the upper limit, if it is then update upper limits
        const prevMonth = getPrevMonth(month, year);

        if (maxBookingMonth.year === year && maxBookingMonth.month === month) {
            maxBookingMonth.month = prevMonth.month;
            maxBookingMonth.year = prevMonth.year;

            setCalMonth(prevMonth.month, prevMonth.year);
            return;
        }

        //if no limits has been reached yet go to the following month
        if (direction === calDirection.FORWARD) {
            setCalMonth(nextMonth.month, nextMonth.year);
        } else {
            setCalMonth(prevMonth.month, prevMonth.year);
        }

        return;
    }

    //set calendar Days of the week and time for slots
    populateCalDays(month, year);

    //set calendar visible
    toggleDateTimePicker();
}

const updateFormBtnsState = () => {
    const nextBtnIcon = document.getElementById('next-btn-icon');
    const submitBtnIcon = document.getElementById('submit-btn-icon');

    if (currentFormStep === 2) {
        formNextButton.querySelector('span').textContent = 'Submit';

        if (submitBtnIcon.classList.contains('hidden')) {
            submitBtnIcon.classList.toggle('hidden');
            nextBtnIcon.classList.toggle('hidden');
        }
    } else {
        formNextButton.querySelector('span').textContent = 'Next';

        if (nextBtnIcon.classList.contains('hidden')) {
            nextBtnIcon.classList.toggle('hidden');
            submitBtnIcon.classList.toggle('hidden');
        }
    }

    if (currentFormStep === 0) {
        formBackButton.disabled = true;
    } else {
        formBackButton.disabled = false;
    }
}

const nextFormStep = async (e) => {
    const cleanInput = (input) => {
        return input.value.replace(/(\s)+/g, ' ').trim();
    }

    if (currentFormStep === 0) {
        let error = false;

        if (!nameValidation(firstName)) {
            error = true;
        }

        if (!nameValidation(lastName)) {
            error = true;
        }

        if (!emailValidation(email)) {
            error = true;
        }

        if (!phoneValidation(phone)) {
            error = true;
        }

        if (!selectValueValidation(service)) {
            error = true;
        }

        if (!selectValueValidation(type)) {
            error = true;
        }

        if (error) {
            formErrorMessage.classList.remove('hidden');
            return;
        }

        formErrorMessage.classList.add('hidden');

        if (type.value === 'business' || type.value === 'both') {
            currentFormStep++;
            personalInfoForm.classList.toggle('hidden');
            businessInfoForm.classList.toggle('hidden');
        }
        else {
            currentFormStep += 2;
            personalInfoForm.classList.toggle('hidden');
            bookingDateForm.classList.toggle('hidden');
        }
    }
    else if (currentFormStep === 1) {
        let error = false;

        if (!nameValidation(companyName, 100)) {
            error = true;
        }

        if (!selectValueValidation(companyAge)) {
            error = true;
        }

        if (!selectValueValidation(companyRevenue)) {
            error = true;
        }

        if (error) {
            formErrorMessage.classList.remove('hidden');
            return;
        }

        formErrorMessage.classList.add('hidden');

        currentFormStep++;
        businessInfoForm.classList.toggle('hidden');
        bookingDateForm.classList.toggle('hidden');
    }
    else if (currentFormStep === 2) {
        const errorMessage = bookingDateForm.querySelector('.error-message');

        if (!selectedTimeSlot.time) {
            formErrorMessage.classList.remove('hidden');
            errorMessage.classList.remove('hidden');
            return;
        }

        formErrorMessage.classList.add('hidden');
        errorMessage.classList.add('hidden');

        const form = document.getElementById('apply-form');
        const formData = new FormData(form);
        formData.append('date', `${selectedTimeSlot.year}-${String(selectedTimeSlot.month).padStart(2, '0')}-${String(selectedTimeSlot.day).padStart(2, '0')}`);
        formData.append('time', selectedTimeSlot.time);
        formNextButton.disabled = true;
        
        try {
            const response = await fetch('/api/book', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(Object.fromEntries(formData))
            });

            if (response.ok) {
                window.location.href = '/success';
            } else {
                const errorData = await response.json();
                const submitErrorMessage = document.getElementById('submit-error');
                submitErrorMessage.classList.remove('hidden');
                console.error('Error submitting application:', errorData.error);
            }
        } catch (error) {
            const submitErrorMessage = document.getElementById('submit-error');
            submitErrorMessage.classList.remove('hidden');
            console.error('Error submitting application:', error);
        }
        formNextButton.disabled = false;
    }

    updateFormBtnsState();
}

const prevFormStep = () => {
    const type = document.getElementById('type').value.trim();

    if (currentFormStep === 2) {
        if (type === 'business') {
            currentFormStep--;
            bookingDateForm.classList.toggle('hidden');
            businessInfoForm.classList.toggle('hidden');
        }
        else {
            currentFormStep -= 2;
            bookingDateForm.classList.toggle('hidden');
            personalInfoForm.classList.toggle('hidden');
        }
    } else {
        currentFormStep--;
        businessInfoForm.classList.toggle('hidden');
        personalInfoForm.classList.toggle('hidden');
    }

    updateFormBtnsState();
    formErrorMessage.classList.add('hidden');
}

const nameValidation = (e, maxLength = 50) => {
    const value = e.value.replace(/(\s)+/g, ' ').trim();
    e.value = value;

    const errorMessage = e.parentElement.querySelector('.error-message');

    if (value.length === 0 || value.length > maxLength) {
        e.classList.add('input-error');
        errorMessage.classList.remove('hidden');
        return false;
    }

    e.classList.remove('input-error');
    errorMessage.classList.add('hidden');

    return true;
}

const emailValidation = (e) => {
    const value = e.value.replace(/(\s)+/g, '').trim();
    e.value = value;

    const errorMessage = e.parentElement.querySelector('.error-message');

    const emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;

    if (!emailRegex.test(value)) {
        e.classList.add('input-error');
        errorMessage.classList.remove('hidden');
        return false;
    }

    e.classList.remove('input-error');
    errorMessage.classList.add('hidden');
    return true;
}

const phoneValidation = (e) => {
    const value = e.value.replace(/(\s)+/g, '').trim();
    e.value = value;

    const errorMessage = e.parentElement.querySelector('.error-message');
    const phoneRegex = /^((\+27)|0)\d{9}$/;

    if (!phoneRegex.test(value)) {
        e.classList.add('input-error');
        errorMessage.classList.remove('hidden');
        return false;
    }

    e.classList.remove('input-error');
    errorMessage.classList.add('hidden');
    return true;
}

const selectValueValidation = (e) => {
    const value = e.value.trim();
    const errorMessage = e.parentElement.querySelector('.error-message');

    if (!value) {
        e.classList.add('input-error');
        errorMessage.classList.remove('hidden');
        return false;
    }

    e.classList.remove('input-error');
    errorMessage.classList.add('hidden');
    return true;
}

//+-----------------------------------------------------------------------------+
//| EVENT LISTINERS                                                             |
//+-----------------------------------------------------------------------------+

//form fields
firstName.addEventListener('blur', (e) => {
    nameValidation(e.target);
});

lastName.addEventListener('blur', (e) => {
    nameValidation(e.target);
});

email.addEventListener('blur', (e) => {
    emailValidation(e.target);
});

phone.addEventListener('blur', (e) => {
    phoneValidation(e.target);
});

service.addEventListener('blur', (e) => {
    selectValueValidation(e.target);
});

service.addEventListener('change', (e) => {
    selectValueValidation(e.target);
});

type.addEventListener('blur', (e) => {
    selectValueValidation(e.target);
});

type.addEventListener('change', (e) => {
    selectValueValidation(e.target);
});

companyName.addEventListener('blur', (e) => {
    if (type.value === 'business' || type.value === 'both') {
        nameValidation(e.target, 100);
    }
});

companyAge.addEventListener('blur', (e) => {
    if (type.value === 'business' || type.value === 'both') {
        selectValueValidation(e.target);
    }
});

companyAge.addEventListener('change', (e) => {
    if (type.value === 'business' || type.value === 'both') {
        selectValueValidation(e.target);
    }
});

companyRevenue.addEventListener('blur', (e) => {
    if (type.value === 'business' || type.value === 'both') {
        selectValueValidation(e.target);
    }
});

companyRevenue.addEventListener('change', (e) => {
    if (type.value === 'business' || type.value === 'both') {
        selectValueValidation(e.target);
    }
});

//form buttons
formNextButton.addEventListener('click', (e) => {
    e.preventDefault();
    nextFormStep(e.target);
});

formBackButton.addEventListener('click', (e) => {
    e.preventDefault();
    prevFormStep();
});

// calendar buttons
calNextMonthButton.addEventListener('click', (e) => {
    e.preventDefault();
    goToNextBookingMonth();
});

calPrevMonthButton.addEventListener('click', (e) => {
    e.preventDefault();
    goToPrevBookingMonth();
});

calRefreshButton.addEventListener('click', (e) => {
    e.preventDefault();
    calRefresh();
});

datePicker.addEventListener('click', (e) => {
    e.preventDefault();

    if (e.target.tagName === 'BUTTON') {
        const date = e.target.dataset.date.split('-');
        selectDate(Number(date[1], 10), Number(date[0], 10), Number(date[2], 10));
    }
});

timePicker.addEventListener('click', (e) => {
    e.preventDefault();

    if (e.target.tagName === 'BUTTON') {
        const dateTime = e.target.dataset.dateTime.split(' ');
        const date = dateTime[0].split('-');
        const activeTime = timePicker.querySelector('.cal-time-active');

        if (activeTime) {
            activeTime.classList.remove('cal-time-active');
            activeTime.disabled = false;
        }

        e.target.classList.add('cal-time-active');
        e.target.disabled = true;

        selectedTimeSlot.year = Number(date[0], 10);
        selectedTimeSlot.month = Number(date[1], 10);
        selectedTimeSlot.day = Number(date[2], 10);
        selectedTimeSlot.time = dateTime[1];

        const oldSDT = datePicker.querySelector('.selected-DT');
        if (oldSDT) {
            oldSDT.classList.remove('selected-DT');
        }

        const currentSDT = Array.from(datePicker.querySelectorAll('.cal-days')).filter((e) => {
            return e.dataset.date == dateTime[0];
        })[0];

        currentSDT.classList.add('selected-DT');

        const timeSelectedDisplay = document.getElementById('time-selected');
        timeSelectedDisplay.textContent = `Selected Date: ${months[selectedTimeSlot.month - 1]} ${selectedTimeSlot.day}, ${selectedTimeSlot.year} at ${selectedTimeSlot.time}`;
        
        const errorMessage = bookingDateForm.querySelector('.error-message');
        errorMessage.classList.add('hidden');
    }
});

//+-----------------------------------------------------------------------------+
//| CODE EXECUTIONS                                                             |
//| This is where code starts executing in order                                |
//+-----------------------------------------------------------------------------+
calRefresh();