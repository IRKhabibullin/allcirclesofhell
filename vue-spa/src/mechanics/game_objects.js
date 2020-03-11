const colors = {
    'tileBackground': '#f0e256',
    'heroMoves': '#5D8AAD',
    'unitMoves': '#EE5A3A',
    'crossMoves': '#E1330D',  // unit's and hero's moves intersection
    'target': '#0f7cdb'
}


class BaseUnit {
    constructor(game_instance, unitData) {
        this.game_instance = game_instance;

        this.name = unitData.name;
        this.health = unitData.health;
        this.armor = unitData.armor;
        this.damage = unitData.damage;
        this.attack_range = unitData.attack_range;
        this.move_range = unitData.move_range;
        this.moves = unitData.moves;
        this.attack_hexes = unitData.attack_hexes;
        this.hex = game_instance.grid.hexes[unitData.position];
        this.img_path = unitData.img_path;
        this.animation_delay = 0; // animation delay. On turn hero should act first, units after his actions.
        this.image = this.game_instance.svg.image(this.img_path);
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
        this.moves = unitData.moves;
        this.attack_hexes = unitData.attack_hexes;
    }

    // animations
    getDamage(damage) {
        this.hex.damage_indicator.text(damage.toString());
        this.hex.damage_indicator
            .animate(100, '-', this.animation_delay).attr({'opacity': 1})
            .animate(1000).font({'opacity': 0}).translate(0, -30)
            .animate(10).translate(0, 0);
    }

    move(target_hex, speed=200) {
        /**
        * Move animation.
        *    destination: hex
        */
        this.hex = target_hex;
        let target_point = target_hex.toPoint();
        this.image.animate(speed, '>', this.animation_delay).move(target_point.x, target_point.y);
    }
    // end animations
};


class Hero extends BaseUnit {
    constructor(game_instance, hero_data) {
        super(game_instance, hero_data);
        this.img_path = './src/assets/board_hero_sized.png';
        this.range_attack_hexes = game_instance.grid.getHexesInRange(this.hex, this.attack_range + 1, ['empty', 'unit']);
        let coords = this.hex.toPoint();
        this.range_weapon = game_instance.svg.circle(5).fill({color: 'black', opacity: 0});
        this.spells = {};
        hero_data.spells.forEach(spell => {
            this.spells[spell.code_name] = spell.effects;
        });
        // suit
        // weapon
    }

    update(unitData, actionData) {
        super.update(unitData, actionData);
        this.game_instance.hero.range_attack_hexes = this.game_instance.grid.getHexesInRange(this.game_instance.hero.hex,
                                                                             this.game_instance.hero.attack_range + 1,
                                                                             ['empty', 'unit']);
        for (var actionName in actionData) {
            this.game_instance.actionManager.handleAction(actionName, this, actionData[actionName]);
        }
        if ('action' in actionData) {
            if (!!this.updateHandler) {
                this.updateHandler();
            }
        }
    }

    showAttackHexes(_show) {
        this.attack_hexes.forEach(hex_id => {
            let element = this.game_instance.grid.hexes[hex_id].polygon;
            if (_show)
                element.classList.add('availableAttackTarget');
            else
                element.classList.remove('availableAttackTarget');
        })
    }

   showRangeAttackHexes(_show) {
        this.range_attack_hexes.forEach(hex_id => {
            let element = this.game_instance.grid.hexes[hex_id].polygon;
            if (_show)
                element.classList.add('availableAttackTarget');
            else
                element.classList.remove('availableAttackTarget');
        })
    }
};


class Unit extends BaseUnit {
    constructor(game_instance, unit_data) {
        super(game_instance, unit_data);
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
        if (!!actionData) {
            for (var actionName in actionData) {
                this.game_instance.actionManager.handleAction(actionName, this, actionData[actionName]);
            }
            if ('action' in actionData) {
                if (!!this.updateHandler) {
                    this.updateHandler(this.hex, actionData);
                }
            }
        }
    }

    mouseoverHandler(event) {
        this.game_instance.show_unit_card = true;
        this.game_instance.current_unit = this;
        if (['attack', 'range_attack'].includes(this.game_instance.selectedAction)) {
            let action_range = 0
            if (this.game_instance.selectedAction == 'attack') {
                action_range = this.game_instance.hero.attack_range;
            } else if (this.game_instance.selectedAction == 'range_attack') {
                action_range = this.game_instance.hero.attack_range + 1;
            }
            if (this.game_instance.grid.distance(this.hex, this.game_instance.hero.hex) <= action_range) {
                document.getElementById(this.hex.q + ';' + this.hex.r).setAttribute('fill', colors.target);
            }
        }
        if (!!this.overTargetHandler) {
            this.overTargetHandler(this.hex);
        }
    }

    mouseoutHandler(event) {
        this.game_instance.show_unit_card = false;
        if (['attack', 'range_attack'].includes(this.game_instance.selectedAction)) {
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

export {Hero, Unit, colors};
