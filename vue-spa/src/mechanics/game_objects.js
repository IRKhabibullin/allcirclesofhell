const colors = {
    'tileBackground': '#f0e256',
    'heroMoves': '#5D8AAD',
    'unitMoves': '#EE5A3A',
    'crossMoves': '#E1330D',  // unit's and hero's moves intersection
    'target': '#0f7cdb'
}


class BaseUnit {
    constructor(board, unitData) {
        this.board = board;

        this.name = unitData.name;
        this.health = unitData.health;
        this.armor = unitData.armor;
        this.damage = unitData.damage;
        this.attack_range = unitData.attack_range;
        this.move_range = unitData.move_range;
        this.moves = unitData.moves;
        this.attack_hexes = unitData.attack_hexes;
        this.hex = board.grid.hexes[unitData.position];
        this.img_path = unitData.img_path;
        this.animation_delay = 0; // animation delay. On turn hero should act first, units after his actions.
        this.image = this.board.svg.image(this.img_path);
        let unit_coords = this.hex.toPoint();
        this.image.move(unit_coords.x, unit_coords.y);
        this.updateHandler = null;
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

        if (unitData.position != (this.hex.q + ';' + this.hex.r)) {
            let new_hex = this.board.grid.hexes[unitData.position];
            this.hex = new_hex;
            this.move(new_hex);
            this.moves = unitData.moves;
            this.attack_hexes = unitData.attack_hexes;
        }
    }

    // animations
    attack(target, damage) {
        /**
        * Attack animation.
        *    target: BaseUnit
        */
        let source_point = this.hex.toPoint();
        let target_point = target.hex.toPoint();
        this.image
            .animate(100, '-', this.animation_delay).move(target_point.x, target_point.y)
            .animate(100, '-').move(source_point.x, source_point.y);
        target.getDamage(damage);
    }

    getDamage(damage) {
        this.hex.damage_indicator.text(damage.toString());
        this.hex.damage_indicator
            .animate(100, '-', this.animation_delay).attr({'opacity': 1})
            .animate(1000).font({'opacity': 0}).translate(0, -30)
            .animate(10).translate(0, 0);
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
        this.img_path = './src/assets/board_hero_sized.png';
        this.range_attack_hexes = board.grid.getHexesInRange(this.hex, this.attack_range + 1, ['empty', 'unit']);
        let coords = this.hex.toPoint();
        this.range_weapon = board.svg.circle(5).fill({color: 'black', opacity: 0});
        this.spells = {};
        hero_data.spells.forEach(spell => {
            this.spells[spell.code_name] = spell.effects;
        });
        // suit
        // weapon
    }

    update(unitData, actionData) {
        super.update(unitData, actionData);
        this.board.hero.range_attack_hexes = this.board.grid.getHexesInRange(this.board.hero.hex,
                                                                             this.board.hero.attack_range + 1,
                                                                             ['empty', 'unit']);
        if ('action' in actionData) {
            if (!!this.updateHandler) {
                this.updateHandler();
            }
            if (actionData['action'] == 'attack') {
                this.attack(this.board.units[actionData.target], actionData.damage);
            } else if (actionData['action'] == 'range_attack') {
                this.range_attack(this.board.units[actionData.target], actionData.damage);
            }
        }
    }

    range_attack(target, damage) {
        /**
        * Range attack animation.
        *    target: BaseUnit
        */
        let source_point = this.hex.toPoint();
        let target_point = target.hex.toPoint();
//        todo move constants like hex_size in separate file and import them from there
        this.range_weapon.move(source_point.x + 30, source_point.y + 30).fill({'opacity': 1})
            .animate(150).fill({'opacity': 0}).move(target_point.x + 30, target_point.y + 30);
        target.hex.damage_indicator.text(damage.toString());
        target.hex.damage_indicator
            .animate(100, '-', this.animation_delay).attr({'opacity': 1})
            .animate(1000).font({'opacity': 0}).translate(0, -30)
            .animate(10).translate(0, 0);
    }

    showAttackHexes(_show) {
        this.attack_hexes.forEach(hex_id => {
            let element = this.board.grid.hexes[hex_id].polygon;
            if (_show)
                element.classList.add('availableAttackTarget');
            else
                element.classList.remove('availableAttackTarget');
        })
    }

   showRangeAttackHexes(_show) {
        this.range_attack_hexes.forEach(hex_id => {
            let element = this.board.grid.hexes[hex_id].polygon;
            if (_show)
                element.classList.add('availableAttackTarget');
            else
                element.classList.remove('availableAttackTarget');
        })
    }
};


class Unit extends BaseUnit {
    constructor(board, unit_data) {
        super(board, unit_data);
        this.pk = unit_data.pk;
        this.animation_delay = 200;

        this.overTargetHandler = null;
        this.outTargetHandler = null;
        this.clickTargetHandler = null;

        this.image.attr('id', 'u_' + unit_data.pk);
        this.image.on('mouseover', this.mouseoverHandler, this);
        this.image.on('mouseout', this.mouseoutHandler, this);
        this.image.on('click', this.clickHandler, this);
    }

    update(unitData, actionData) {
        super.update(unitData, actionData);
        if ('action' in actionData) {
            if (actionData.action == 'attack') {
                this.attack(this.board.hero, actionData.damage);
            }
            if (!!this.updateHandler) {
                this.updateHandler(this.hex, actionData);
            }
        }
    }

    mouseoverHandler(event) {
        this.board.show_unit_card = true;
        this.board.current_unit = this;
        if (['attack', 'range_attack'].includes(this.board.selectedAction)) {
            let action_range = 0
            if (this.board.selectedAction == 'attack') {
                action_range = this.board.hero.attack_range;
            } else if (this.board.selectedAction == 'range_attack') {
                action_range = this.board.hero.attack_range + 1;
            }
            if (this.board.grid.distance(this.hex, this.board.hero.hex) <= action_range) {
                document.getElementById(this.hex.q + ';' + this.hex.r).setAttribute('fill', colors.target);
            }
        }
        if (!!this.overTargetHandler) {
            this.overTargetHandler(this.hex);
        }
    }

    mouseoutHandler(event) {
        this.board.show_unit_card = false;
        if (['attack', 'range_attack'].includes(this.board.selectedAction)) {
            document.getElementById(this.hex.q + ';' + this.hex.r).setAttribute('fill', this.hex.image);
        }
        if (!!this.outTargetHandler) {
            this.outTargetHandler(this.hex);
        }
    }

    clickHandler(event) {
        if (!!this.clickTargetHandler) {
            this.clickTargetHandler(this);
        }
    }
};


class Structure {
    constructor(board, structureData) {
        this.board = board;

        this.name = structureData.name;
        this.code_name = structureData.code_name;
        this.img_path = structureData.img_path;
        this.hex = board.grid.hexes[structureData.position];
        this.image = this.board.svg.image(this.img_path, 55, 55);
        let structure_coords = this.hex.toPoint();
        this.image.move(structure_coords.x, structure_coords.y);

        this.clickTargetHandler = null;

        this.image.on('click', this.clickHandler, this);
    }

    clickHandler(event) {
        if (!!this.clickTargetHandler) {
            this.clickTargetHandler(this.hex);
        }
    }
};

export {Hero, Unit, colors, Structure};
