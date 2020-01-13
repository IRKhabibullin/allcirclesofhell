import {Hero, Unit} from './game_objects';
import HexGrid from './grid';
import ActionManager from './actions';

const colors = {
    'tileBackground': '#f0e256',
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

        this.actionManager = new ActionManager(this);
        this.actionManager.setAction('move');

        this.current_unit = false;
        this.show_unit_card = false;  // variable for UnitCard element in Vue component
        this.altPressed = false;
    }

    handleAction(actionData) {
        if (actionData.allowed) {
            // update hexes on board
            for (var _hex_id in actionData.board.hexes) {
                let _hex = actionData.board.hexes[_hex_id];
                let current_hex = this.grid.getHexByCoords(_hex.q, _hex.r);
                if (current_hex.occupied_by != _hex.occupied_by) {
                    let class_to_remove = current_hex.occupied_by == 'empty' ? 'hex' : 'obstacle_hex';
                    let class_to_add = _hex.occupied_by == 'empty' ? 'hex' : 'obstacle_hex';
                    if (class_to_add != class_to_remove) {
                        document.getElementById(current_hex.q + ';' + current_hex.r).classList.remove(class_to_remove);
                        document.getElementById(current_hex.q + ';' + current_hex.r).classList.add(class_to_add);
                    }
                    current_hex.occupied_by = _hex.occupied_by;
                }
            }
            console.log('actionData', actionData);
            this.actionManager.handleAction(actionData.action_data);
            this.actionManager.changeAction('move');
            this.hero.update(actionData.game.hero, actionData.action_data);
            this.update_units(actionData.units, actionData.units_actions);
        }
    }

    update_units(new_units, units_actions) {
        let units_to_add = Object.keys(new_units).filter(u => !(u in this.units));
        let units_to_update = Object.keys(this.units).filter(u => u in new_units);
        let units_to_remove = Object.keys(this.units).filter(u => !(u in new_units));

        units_to_update.forEach(unit_id => {
            this.units[unit_id].update(new_units[unit_id], {'action': new_units[unit_id].action,
                                                            'damage': new_units[unit_id].damage_dealt});
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
            unit.attack_hexes.forEach(hex_id => {
                document.getElementById(hex_id)
                    .setAttribute('fill', this.hero.moves.includes(hex_id) ? colors.crossMoves : colors.unitMoves);
            })
        };
        this.grid.coordinates.attr('opacity', 1);
    }

    hideMoves() {
        for (var unit_id in this.units) {
            let unit = this.units[unit_id];
            unit.attack_hexes.forEach(hex_id => {
                this.grid.hexes[hex_id].setCurrentBackground();
            })
        };
        this.hero.moves.forEach(hex_id => {
            this.grid.hexes[hex_id].setCurrentBackground();
        });
        this.grid.coordinates.attr('opacity', 0);
    }
}

export default Board
