// static/js/script.js

// พร้อมใช้งาน DOM
document.addEventListener('DOMContentLoaded', function() {
    // แสดงปุ่มยืนยันการลบ
    setupDeleteConfirmation();
    
    // จัดการกับการแสดงแจ้งเตือน (Alert)
    setupAlertDismiss();
    
    // เพิ่มฟีเจอร์ค้นหาและกรองข้อมูล
    setupSearchFilters();
    
    // จัดการกับการป้อนฟอร์ม
    setupFormValidation();
    
    // นำเข้าฟอนต์ Sarabun สำหรับภาษาไทย
    loadSarabunFont();
});

// ฟังก์ชันโหลดฟอนต์ Sarabun
function loadSarabunFont() {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'https://fonts.googleapis.com/css2?family=Sarabun:wght@400;500;600;700&display=swap';
    document.head.appendChild(link);
}

// ฟังก์ชันตั้งค่าการยืนยันการลบ
function setupDeleteConfirmation() {
    // หาปุ่มลบทั้งหมด
    const deleteButtons = document.querySelectorAll('.btn-delete');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('คุณแน่ใจหรือไม่ที่ต้องการลบข้อมูลนี้?')) {
                e.preventDefault();
            }
        });
    });
}

// ฟังก์ชันตั้งค่าการปิดแจ้งเตือน
function setupAlertDismiss() {
    // หากมีการเรียกใช้งาน Bootstrap 5 จะแสดงปุ่มปิดอัตโนมัติ
    // แต่หากต้องการให้ปิดเองอัตโนมัติหลังจาก 5 วินาที:
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

// ฟังก์ชันตั้งค่าการค้นหาและกรอง
function setupSearchFilters() {
    // หาฟอร์มค้นหาทั้งหมด
    const searchForms = document.querySelectorAll('.search-form');
    
    searchForms.forEach(form => {
        // เมื่อกดปุ่มล้างข้อมูล
        const resetBtn = form.querySelector('.btn-reset');
        if (resetBtn) {
            resetBtn.addEventListener('click', function() {
                const inputs = form.querySelectorAll('input, select');
                inputs.forEach(input => {
                    if (input.type === 'text' || input.type === 'search' || input.tagName === 'SELECT') {
                        input.value = '';
                    }
                });
                
                // ส่งฟอร์มหลังจากล้างข้อมูล
                form.submit();
            });
        }
        
        // อัปเดตการค้นหาอัตโนมัติเมื่อเลือกตัวกรอง
        const autoSubmitInputs = form.querySelectorAll('.auto-submit');
        autoSubmitInputs.forEach(input => {
            input.addEventListener('change', function() {
                form.submit();
            });
        });
    });
}

// ฟังก์ชันตั้งค่าการตรวจสอบฟอร์ม
function setupFormValidation() {
    // หาฟอร์มทั้งหมดที่ต้องการตรวจสอบ
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
    
    // ตรวจสอบเลขบัตรประชาชน
    const idCardInputs = document.querySelectorAll('.id-card-input');
    idCardInputs.forEach(input => {
        input.addEventListener('input', function() {
            // ปรับให้เป็นตัวเลขเท่านั้น
            this.value = this.value.replace(/[^0-9]/g, '');
            
            // จำกัดความยาวสูงสุด 13 หลัก
            if (this.value.length > 13) {
                this.value = this.value.slice(0, 13);
            }
        });
    });
    
    // ตรวจสอบเบอร์โทรศัพท์
    const phoneInputs = document.querySelectorAll('.phone-input');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function() {
            // ปรับให้เป็นตัวเลขเท่านั้น
            this.value = this.value.replace(/[^0-9]/g, '');
            
            // จำกัดความยาวสูงสุด 10 หลัก
            if (this.value.length > 10) {
                this.value = this.value.slice(0, 10);
            }
        });
    });
}