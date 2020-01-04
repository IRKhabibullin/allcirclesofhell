class BaseUnit {
    constructor(board, unit_data) {
        this.board = board;

        this.name = unit_data.name;
        this.health = unit_data.health;
        this.armor = unit_data.armor;
        this.damage = unit_data.damage;
        this.attack_range = unit_data.attack_range;
        this.move_range = unit_data.move_range;
        let moves = [];
        unit_data.moves.forEach(_pos => {
            moves.push(board.grid.hexes[_pos]);
        });
        this.moves = moves;
        let attack_hexes = [];
        unit_data.attack_hexes.forEach(_pos => {
            attack_hexes.push(board.grid.hexes[_pos]);
        });
        this.attack_hexes = attack_hexes;
        this.hex = board.grid.hexes[unit_data.position];
        this.img_path = unit_data.img_path;
        this.animation_delay = 0; // animation delay. On turn hero should act first, units after his actions.
        this.image = this.board.svg.image(this.img_path);
        let unit_coords = this.hex.toPoint();
        this.image.move(unit_coords.x, unit_coords.y);
        // skills
        // spells
    }

    update(unitData, actionData) {
        /**
        * Update unit state after turn made.
        *    unit_data: Object
        */
        this.health = unitData.health;
        this.armor = unitData.armor;
        this.damage = unitData.damage;
        this.attack_range = unitData.attack_range;
        this.move_range = unitData.move_range;

        if (unitData.position != [this.hex.q, this.hex.r]) {
            let new_hex = this.board.grid.hexes[unitData.position];
            this.hex = new_hex;
            this.move(new_hex);
            let moves = [];
            unitData.moves.forEach(_pos => {
                moves.push(this.board.grid.hexes[_pos]);
            });
            this.moves = moves;
            let attack_hexes = [];
            unitData.attack_hexes.forEach(_pos => {
                attack_hexes.push(this.board.grid.hexes[_pos]);
            });
            this.attack_hexes = attack_hexes;
        }
    }

    // animations
    attack(target) {
        /**
        * Attack animation.
        *    target: BaseUnit
        */
        let source_point = this.hex.toPoint();
        let target_point = target.hex.toPoint();
        this.image
            .animate(100, '-', this.animation_delay).move(target_point.x, target_point.y)
            .animate(100, '-').move(source_point.x, source_point.y);
    }

    move() {
        /**
        * Move animation.
        *    destination: hex
        */
        let coords = this.hex.toPoint();
        this.image.animate(200, '>', this.animation_delay).move(coords.x, coords.y);
    }
    // end animations
};


class Hero extends BaseUnit {
    constructor(board, hero_data) {
        super(board, hero_data);
        this.path = [];
        this.img_path = './src/assets/board_hero_sized.png';
        // suit
        // weapon
    }

    update(unitData, actionData) {
        super.update(unitData, actionData);
        if ('action' in actionData) {
            if (actionData['action'] == 'move') {
                this.resetPath();
            } else if (actionData['action'] == 'attack') {
                this.attack(this.board.units[actionData.target]);
            }
        }
    }

    resetPath() {
        this.path.forEach(hex => {
            hex.image = hex.getBackground('empty');
            document.getElementById(hex.q + ';' + hex.r).setAttribute('fill', hex.image);
        })
//            probably need to save calculated path and look here for another var like "path_chosen"
        this.path = [];
    }

    buildPath(destination) {
        this.path = this.board.grid.findPath(this.hex, destination);
        this.path.forEach(hex => {
            hex.image = hex.getBackground('path');
            document.getElementById(hex.q + ';' + hex.r).setAttribute('fill', hex.image);
        })
    }
};


class Unit extends BaseUnit {
    constructor(board, unit_data) {
        super(board, unit_data);
        this.pk = unit_data.pk;
        this.animation_delay = 200;
        this.image.attr('id', 'u_' + unit_data.pk);
        this.image.on('mouseover', this.mouseoverHandler, this);
        this.image.on('mouseout', this.mouseoutHandler, this);
        this.image.on('click', this.clickHandler, this);
    }

    update(unitData, actionData) {
        super.update(unitData, actionData);
        if ('action' in actionData && actionData['action'] == 'attack') {
            this.attack(this.board.hero);
        }
    }

    mouseoverHandler(event) {
        this.board.show_unit_card = true;
        this.board.current_unit = this;
        if (this.board.selectedAction == 'attack') {
            if (this.board.grid.distance(this.hex, this.board.hero.hex) <= this.board.hero.attack_range) {
                document.getElementById(this.hex.q + ';' + this.hex.r).setAttribute('fill', this.board.colors.target);
            }
        }
    }

    mouseoutHandler(event) {
        this.board.show_unit_card = false;
        if (this.board.selectedAction == 'attack') {
            document.getElementById(this.hex.q + ';' + this._hex.r).setAttribute('fill', this.hex.image);
        }
    }

    clickHandler(event) {
        document.getElementById(this.hex.q + ';' + this.hex.r).setAttribute('fill', this.hex.image);

        if (this.board.grid.distance(this.hex, this.board.hero.hex) <= this.board.hero.attack_range) {
            this.board.component.makeAction({'action': 'attack', 'target': this.pk});
        } else if (this.board.hero.path.length > 0) {
            if (this.hex != this.board.hero.path[0]) {
                this.board.hero.resetPath();
                this.board.hero.buildPath(this.hex);
            } else {
                let hex_in_path = this.board.hero.path[this.board.hero.path.length - 1];
                this.board.component.makeAction({'action': 'move', 'destination': hex_in_path.q + ';' + hex_in_path.r});
            }
        } else {
            this.board.hero.buildPath(this.hex);
        }
    }
};

export {Hero, Unit};
