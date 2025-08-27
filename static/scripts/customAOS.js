const popUpElements = document.querySelectorAll('.aos, .aos-c');

const options = {
    root: null,
    rootMargin: '0px',
    threshold: 0.25  //Trigger when 25% of the element is visible
};

const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const target = entry.target;

            if (target.classList.contains('aos')) {
                target.classList.add('visible');
                target.classList.remove('hidden');
            }
            else {
                const childAos = target.querySelector('.aos');
                if (childAos) {
                    childAos.classList.add('visible');
                    childAos.classList.remove('hidden');
                }
            }

            //stop observing the element
            observer.unobserve(entry.target);
        } 
    });
}, options);

popUpElements.forEach(element => {
   observer.observe(element);
});
