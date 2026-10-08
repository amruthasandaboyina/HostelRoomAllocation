function confirmDelete(type) {
    return confirm("Are you sure you want to " + (type === "allocation" ? "cancel this allocation" : "delete this " + type) + "?");
}

function validateStudentForm() {
    const form = document.querySelector("form");
    const phone = form.phone.value.trim();
    const email = form.email.value.trim();
    const year = Number(form.year.value);
    if (!form.name.value.trim() || !form.course.value.trim()) {
        alert("Name and course are required.");
        return false;
    }
    if (year < 1 || year > 6) {
        alert("Year must be between 1 and 6.");
        return false;
    }
    if (!/^\d{10,15}$/.test(phone)) {
        alert("Phone must contain 10 to 15 digits.");
        return false;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        alert("Enter a valid email address.");
        return false;
    }
    return true;
}

function validateRoomForm() {
    const form = document.querySelector("form");
    if (!form.room_number.value.trim() || !form.block.value.trim()) {
        alert("Room number and block are required.");
        return false;
    }
    if (Number(form.floor.value) < 0) {
        alert("Floor must be zero or greater.");
        return false;
    }
    if (Number(form.capacity.value) <= 0) {
        alert("Capacity must be greater than zero.");
        return false;
    }
    return true;
}

function validateAllocationForm() {
    const form = document.querySelector("form");
    if (!form.student_id.value || !form.room_id.value || !form.allocation_date.value) {
        alert("Please select a student, room and date.");
        return false;
    }
    return true;
}

setTimeout(() => {
    document.querySelectorAll(".flash").forEach(el => {
        el.style.opacity = "0";
        el.style.transition = "opacity .5s";
        setTimeout(() => el.remove(), 500);
    });
}, 4500);
