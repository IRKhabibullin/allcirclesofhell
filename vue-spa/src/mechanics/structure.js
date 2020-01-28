class PriorityQueue {
    constructor() {
        this.container = [];
    }
    display() {
        console.log(this.container);
    }
    isEmpty() {
        return this.container.length === 0;
    }
    size() {
        return this.container.length
    }
    push(hex, priority) {
        let currElem = new this.Element(hex, priority);
        let addedFlag = false;
        for (let i = 0; i < this.container.length; i++) {
            if (currElem.priority < this.container[i].priority) {
                this.container.splice(i, 0, currElem);
                addedFlag = true;
                break;
            }
        }
        if (!addedFlag) {
            this.container.push(currElem);
        }
    }
    peek() {
        return this.container.pop().hex;
    }
    pop() {
        return this.container.shift().hex;
    }
    clear() {
        this.container = [];
    }
}

PriorityQueue.prototype.Element = class {
    constructor(hex, priority) {
        this.hex = hex;
        this.priority = priority;
    }
};

export default PriorityQueue
