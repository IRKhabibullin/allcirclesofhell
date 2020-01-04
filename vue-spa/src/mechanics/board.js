import {Hero, Unit} from './game_objects';
import HexGrid from './grid';

const colors = {
    'tileBackground': '#f0e256',
    'path': 'green',
    'heroMoves': '#5D8AAD',
    'unitMoves': '#EE5A3A',
    'crossMoves': '#E1330D',  // unit's and hero's moves intersection
    'target': '#0f7cdb'
}

class Board {
    /**
    * Class to work with game board
    */
    constructor(component, svg_field, board_data, units, hero_data) {
        this.component = component;
        this.svg = svg_field;
        this.grid = new HexGrid(this, board_data.radius, board_data.hexes);


        this.hero = new Hero(this, hero_data);

        this.units = {};
        for (var unit_id in units) {
            this.units[unit_id] = new Unit(this, units[unit_id]);
        }
        this.current_unit = false;
        this.show_unit_card = false;  // variable for UnitCard element in Vue component
        this.selectedAction = 'move';
        this.altPressed = false;
    }

    handleAction(actionData) {
        if (actionData.allowed) {
            // update hexes on board
            for (var _hex_id in actionData.board.hexes) {
                let _hex = actionData.board.hexes[_hex_id];
                let current_hex = this.grid.getHexByCoords(_hex.q, _hex.r);
                if (current_hex.occupied_by != _hex.occupied_by) {
                    let class_to_remove = current_hex.occupied_by == 'empty' ? 'comb' : 'obstacle_comb';
                    let class_to_add = _hex.occupied_by == 'empty' ? 'comb' : 'obstacle_comb';
                    if (class_to_add != class_to_remove) {
                        document.getElementById(current_hex.q + ';' + current_hex.r).classList.remove(class_to_remove);
                        document.getElementById(current_hex.q + ';' + current_hex.r).classList.add(class_to_add);
                    }
                    current_hex.occupied_by = _hex.occupied_by;
                }
            }
            this.hero.update(actionData.game.hero, {'action': actionData.action, 'target': actionData.target});
            this.update_units(actionData.units, actionData.units_actions);
        }
    }

    update_units(new_units, units_actions) {
        let units_to_add = Object.keys(new_units).filter(u => !(u in this.units));
        let units_to_update = Object.keys(this.units).filter(u => u in new_units);
        let units_to_remove = Object.keys(this.units).filter(u => !(u in new_units));

        units_to_update.forEach(unit_id => {
            this.units[unit_id].update(new_units[unit_id], {'action': new_units[unit_id].action});
        });
        units_to_remove.forEach(unit_id => {
            this.units[unit_id].image.remove();
            delete this.units[unit_id];
        });
        units_to_add.forEach(unit_id => {
            this.units[unit_id] = new Unit(this, new_units[unit_id]);
        })
    }

    showMoves() {
        this.hero.moves.forEach(_hex => {
            document.getElementById(_hex.q + ';' + _hex.r).setAttribute('fill', colors.heroMoves);
        });
        for (var unit_id in this.units) {
            let unit = this.units[unit_id];
            unit.attack_hexes.forEach(hex => {
                document.getElementById(hex.q + ';' + hex.r)
                    .setAttribute('fill', this.hero.moves.includes(hex) ? colors.crossMoves : colors.unitMoves);
            })
        };
    }

    hideMoves() {
        for (var unit_id in this.units) {
            let unit = this.units[unit_id];
            unit.attack_hexes.forEach(hex => {
                hex.setCurrentBackground();
            })
        };
        this.hero.moves.forEach(_hex => {
            _hex.setCurrentBackground();
        });
    }

    actionSelected(actionName) {
        this.selectedAction = actionName;
    }
}

export default Board
